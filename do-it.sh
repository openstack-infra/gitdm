#!/bin/bash

GITBASE=~/git/openstack
RELEASE=folsom
BASEDIR=$(pwd)
CONFIGDIR=$(pwd)/openstack-config
TEMPDIR=$(mktemp -d $(pwd)/dmtmp-XXXXXX)
GITLOGARGS="--no-merges --numstat -M --find-copies-harder"

if [ ! -d .venv ]; then
    echo "Creating a virtualenv"
    ./tools/install_venv.sh
fi

echo "Updating projects from git"
grep -v '^#' ${CONFIGDIR}/${RELEASE} |
    while read project x; do
      cd ${GITBASE}/${project}
      git fetch origin 2>/dev/null
    done

echo "Generating git commit logs"
grep -v '^#' ${CONFIGDIR}/${RELEASE} |
    while read project revisions excludes x; do
        cd ${GITBASE}/${project}
        git log ${GITLOGARGS} ${revisions} > "${TEMPDIR}/${project}-commits.log"
        if [ -n "$excludes" ]; then
            awk "/^commit /{ok=1} /^commit ${excludes}/{ok=0} {if(ok) {print}}" \
                < "${TEMPDIR}/${project}-commits.log" > "${TEMPDIR}/${project}-commits.log.new"
            mv "${TEMPDIR}/${project}-commits.log.new" "${TEMPDIR}/${project}-commits.log"
        fi
    done

echo "Generating git statistics"
cd ${BASEDIR}
grep -v '^#' ${CONFIGDIR}/${RELEASE} |
    while read project x; do
        python gitdm -l 20 -n < "${TEMPDIR}/${project}-commits.log" > "${TEMPDIR}/${project}-git-stats.txt"
    done

grep -v '^#' ${CONFIGDIR}/${RELEASE} |
    while read project x; do
        cat "${TEMPDIR}/${project}-commits.log" >> "${TEMPDIR}/git-commits.log"
    done
python gitdm -l 20 -n < "${TEMPDIR}/git-commits.log" > "${TEMPDIR}/git-stats.txt"

echo "Generating a list of bugs"
cd ${BASEDIR}
grep -v '^#' ${CONFIGDIR}/${RELEASE} |
    while read project x; do
        ./tools/with_venv.sh python launchpad/buglist.py ${project} ${RELEASE} > "${TEMPDIR}/${project}-bugs.log"
        while read id person date x; do
            emails=$(awk "/^$person / {print \$2}" ${CONFIGDIR}/launchpad-ids.txt)
            echo $id $person $date $emails
        done < "${TEMPDIR}/${project}-bugs.log" > "${TEMPDIR}/${project}-bugs.log.new"
        mv "${TEMPDIR}/${project}-bugs.log.new" "${TEMPDIR}/${project}-bugs.log"
    done

echo "Generating launchpad statistics"
cd ${BASEDIR}
grep -v '^#' ${CONFIGDIR}/${RELEASE} |
    while read project x; do
        grep -v '<unknown>' "${TEMPDIR}/${project}-bugs.log" |
            python lpdm -l 20 > "${TEMPDIR}/${project}-lp-stats.txt"
    done

grep -v '^#' ${CONFIGDIR}/${RELEASE} |
    while read project x; do
        grep -v '<unknown>' "${TEMPDIR}/${project}-bugs.log" >> "${TEMPDIR}/lp-bugs.log"
    done
grep -v '<unknown>' "${TEMPDIR}/lp-bugs.log" |
    python lpdm -l 20 > "${TEMPDIR}/lp-stats.txt"

echo "Generating a list of Change-Ids"
grep -v '^#' ${CONFIGDIR}/${RELEASE} |
    while read project revisions x; do
        cd "${GITBASE}/${project}"
        git log ${revisions} |
            awk '/^    Change-Id: / { print $2 }' |
            split -l 100 -d - "${TEMPDIR}/${project}-${RELEASE}-change-ids-"
    done

cd ${TEMPDIR}
grep -v '^#' ${CONFIGDIR}/${RELEASE} |
    while read project x; do
        > ${project}-${RELEASE}-reviews.json
        for f in ${project}-${RELEASE}-change-ids-??; do
            echo "Querying gerrit: ${f}"
            ssh -p 29418 review.openstack.org \
                gerrit query --all-approvals --format=json \
                $(awk -v ORS=' OR '  '{print}' $f | sed 's/ OR $//') \
                < /dev/null >> "${project}-${RELEASE}-reviews.json"
        done
    done

echo "Generating a list of commit IDs"
grep -v '^#' ${CONFIGDIR}/${RELEASE} |
    while read project revisions x; do
        cd "${GITBASE}/${project}"
        git log --pretty=format:%H $revisions > \
            "${TEMPDIR}/${project}-${RELEASE}-commit-ids.txt"
    done

echo "Parsing the gerrit queries"
cd ${BASEDIR}
grep -v '^#' ${CONFIGDIR}/${RELEASE} |
    while read project x; do
        python gerrit/parse-reviews.py \
            "${TEMPDIR}/${project}-${RELEASE}-commit-ids.txt" \
            "${CONFIGDIR}/launchpad-ids.txt" \
            < "${TEMPDIR}/${project}-${RELEASE}-reviews.json"  \
            > "${TEMPDIR}/${project}-${RELEASE}-reviewers.txt"
    done

echo "Generating gerrit statistics"
cd ${BASEDIR}
grep -v '^#' ${CONFIGDIR}/${RELEASE} |
    while read project x; do
        python gerritdm -l 20 \
            < "${TEMPDIR}/${project}-${RELEASE}-reviewers.txt" \
            > "${TEMPDIR}/${project}-gerrit-stats.txt"
    done

> "${TEMPDIR}/gerrit-reviewers.txt"
grep -v '^#' ${CONFIGDIR}/${RELEASE} |
    while read project x; do
        cat "${TEMPDIR}/${project}-${RELEASE}-reviewers.txt" >> "${TEMPDIR}/gerrit-reviewers.txt"
    done
python gerritdm -l 20 < "${TEMPDIR}/gerrit-reviewers.txt" > "${TEMPDIR}/gerrit-stats.txt"

cd ${BASEDIR}
rm -rf ${RELEASE} && mkdir ${RELEASE}
mv ${TEMPDIR}/*stats.txt ${RELEASE}
rm -rf ${TEMPDIR}
