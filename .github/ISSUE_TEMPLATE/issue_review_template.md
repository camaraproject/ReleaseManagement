---
name: 💡 Review 🌟
about: Request the review of a given issue or PR by the Release Mgmt team
title: '$repo name$ $releasenr$ ($mile-stone or type of release$) release review'
labels: 'review'
assignees: ''

---
<!-- Examples for $mile-stone or type of release$ in issue title: 
* "$meta-release$ M4" (e.g. "Spring25 M4")
* "$meta-release$ M3" (e.g. "Fall25 M3")
* "Sandbox pre-release (review by Release Management is optional)
* Sandbox public release
* Fall24 Patch pre-release (review by Release Management is optional)
* Fall24 Patch public release
-->

**Release PR to review**
<!-- Put here the link to the releae PR that need to be reviewed -->

- ...

**Related release tracker pages in wiki**
<!-- Put here the link(s) to the release trackers of the API versions which will (pre)-released with the release PR -->

- ...
- ...

**Review actions**

Assign this issue to yourself and follow the below list.
For any review action, review the file(s) in the issue/PR listed above. 
Put comments in the above issue or PR if they concern non-changed files/text.
Put a short summary of the main review result here into the review issue.

- [ ] API release tracker page(s) available on wiki (add link(s) above)
- [ ] API definition files (YAML) (check version in info & servers objects)  
- [ ] test definition file(s) (check availability and version infos)
- [ ] changelog updated
- [ ] readme updated (check correct release number / API version naming) 
- [ ] API readiness checklist(s) (check consistency with artefacts in the repository and PR)

**Release actions**

Assign this issue to yourself or another RM team member and follow the below list. 
When done, tick the box in this issue. 

- [ ] Short link to release review issue added to release trackers (by RM, for M3/M4 reviews)
- [ ] Review comments provided (on behalf of Release Management)
- [ ] Review comments addressed (by Sub Project)
- [ ] Release PR approved (on behalf of Release Management)
- [ ] PR merged (by Sub Project codeowner)
- [ ] Release created within GitHub (by Sub Project codeowner)
- [ ] Release Tracker updated (with creation date of the release and the release tag link)

**Additional comments**
<!-- Add any other comments here as needed. -->
