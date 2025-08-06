---
name: 💡 Fall25 M4 Review 🌟
about: Request the review of a Fall25 M4 release PR by the Release Mgmt team
title: '$repo name$ $releasenr$ (Fall25 M4) release review'
labels: 'Fall25 M4 review'
assignees: ''

---


**Release PR to review**
<!-- Put here the link to the release PR that need to be reviewed -->

- 

**Related release tracker pages in wiki**
<!-- Put here the link(s) to the release trackers of the API versions which will (pre)-released with the release PR -->

- 
- 

# Review actions

### API repository
- [ ] Check that there are no PRs beside the release PR are waiting to be reviewed and merged. If there are other open PRs, request that they are either set to draft (if not relevant for Fall25) or merged and the release PR get updated before the review

### CHANGELOG.MD 
**Table of contents**
- [ ] the `y` in `rX.Y` has been increased by 1 from the pre-release 

**Release notes**
- [ ] first paragraph: 'public release' is used instead of 'pre-release'
- [ ] the release candidate suffix (`-rc.x`) has been removed from API versions
- [ ] the release candidate suffix (`-rc.x`) has been removed from Commonalities and ICM versions

**API sections of CHANGELOG**
- [ ] the words 'release candidate' are not present
- [ ] the release candidate suffix (`-rc.x`) has been removed from API versions
- [ ] API definition links {ReDoc, Swagger, OAS) includes the correct release tag in the URL
- [ ] Added/Changed/Removed sections includes any additional changes made for M4 and all the entries from M3
- _Note: create a "draft release" to see which PRs were done since the last document pre-release `rX.Y`_

### API definition .yaml file(s)
- [ ] `info.version` has been updated to latest version number (without rc.n suffix)
- [ ] `info.servers.url` has been updated to include latest version number (without rc.n suffix)
- [ ] check for links containing `/main/` or `/rX.Y/` (with `rX.Y` being the pre-release) which are pointing the repository. They must be replaced with the `/rX.Y+1/`.
- [ ] Read the Swagger UI view of the API yaml to spot formatting/spelling errors

### Test definition .feature file(s)
- [ ] 'Feature:' line: `vwip` has been changed to the latest version number
- [ ] All resource links have been updated with the correct serverURL and are using a root-relative path (e.g. `And the resource "/qos-profiles/vwip/qos-profiles/{name}"`)

### API Readiness checklist
- [ ] first line ('Checklist for'): has been updated to the latest version number and the latest release number
- [ ] links to Commonalities and ICM r3.3

### README.MD
- [ ] the 'NEW: public release' section is updated with the latest release number
- [ ] The ReDoc/Swagger/OAS links have been updated with the latest release number in their URL
- [ ] the 'NEW: Pre-release' section has been removed

### API description wiki page
- [ ] Check that the links within API Readiness Checklists are pointing to valid wiki pages
- [ ] Co-assign the review issue to a member of the API Backlog team (tbd to whom!)
- [ ] Get confirmation from API Backlog team that the API description is up-to-date

# Release actions

Assign this issue to yourself or another RM team member and follow the below list. 
When done, tick the box in this issue (requires write access, leave a comment otherwise). 

- [ ] Short link to release review issue added to release trackers ("M4 #nnn")
- [ ] Review comments provided (on behalf of Release Management)
- [ ] Review comments addressed (by release PR editor)
- [ ] `/rc-api-review` run by Release Management reviewer as final check
- [ ] Release PR approved (on behalf of Release Management)
- [ ] PR merged (by API repository codeowner)
- [ ] Release created within GitHub (by API repository codeowner)
- [ ] Release Tracker updated (with creation date of the release and the release tag link)

(Note: For public releases within Fall25 M4 the updates of GitHub README, CAMARA website and within API Backlog list will be done in batch as part of M5 milestone.)

**Additional comments**
<!-- Add any other comments here as needed. -->
