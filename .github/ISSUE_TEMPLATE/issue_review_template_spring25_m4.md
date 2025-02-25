---
name: 💡 Spring M4 Review 🌟
about: Request the review of a Spring25 M4 release PR by the Release Mgmt team
title: '$repo name$ $releasenr$ (Spring25 M4) release review'
labels: 'Spring25 M4 review'
assignees: ''

---


**Release PR to review**
<!-- Put here the link to the release PR that need to be reviewed -->

- 

**Related release tracker pages in wiki**
<!-- Put here the link(s) to the release trackers of the API versions which will (pre)-released with the release PR -->

- 
- 

**Review actions**

Assign this issue to yourself and follow the below list.
For any review action, review the file(s) in the issue/PR listed above. 
Put comments in the above issue or PR if they concern non-changed files/text.
Put a short summary of the main review result as a comment here into the review issue.

- [ ] API definition files updated (YAML) (version in info & servers objects, check for links into main or older releases)  
- [ ] test definition file(s) (availability, version infos and resource URLs)
- [ ] changelog updated (structure in line with template, for public release all changes since last public release must be listed, Commonalities & ICM public releases)
- [ ] readme updated (correct naming "Public release" and release number, API versions naming, alignment with template) 
- [ ] API readiness checklist(s) (check link to Commonalities and ICM r2.3, for stable APIs, check for link to "test result statement" issue)

Specific checks for APIs with subscriptions/notifications, that the following PRs are applied to be aligned with Commonalities r2.3:
- [ ] Added note and changed descriptions for date-time formats in subscriptions in [#404](https://github.com/camaraproject/Commonalities/pull/404)
- [ ] Sink format corrected in [#414](https://github.com/camaraproject/Commonalities/pull/414/files) and [#421](https://github.com/camaraproject/Commonalities/pull/421) (from `url` to `uri`)
- [ ] Error 429 aligned for event-subscription-template.yaml and notification-as-cloud-event.yaml in [#407](https://github.com/camaraproject/Commonalities/pull/407/files) and [#408](https://github.com/camaraproject/Commonalities/pull/408/files)
- [ ] Removed sinkCredential from Subscription schema in event-subscription-template.yaml in [#400](https://github.com/camaraproject/Commonalities/pull/400) (The sinkCredential must not be present in POST and GET responses)

Specific request to API Repositories promoted to "Incubating" stage:
- [ ] Badge "Incubating API Repository" applied in README
- [ ] Text in README aligned with [template README.md](https://github.com/camaraproject/Template_API_Repository/blob/main/README.md) (see code)
- [ ] Line "Incubating stage since: February 2025" added

**Release actions**

Assign this issue to yourself or another RM team member and follow the below list. 
When done, tick the box in this issue (requires write access, leave a comment otherwise). 

- [ ] Short link to release review issue added to release trackers ("M4 #nnn")
- [ ] Review comments provided (on behalf of Release Management)
- [ ] Review comments addressed (by release PR editor)
- [ ] Release PR approved (on behalf of Release Management)
- [ ] PR merged (by API repository codeowner)
- [ ] Release created within GitHub (by API repository codeowner)
- [ ] Release Tracker updated (with creation date of the release and the release tag link)

Note: for public releases within Spring25 M4 the updates of GitHub README, CAMARA website and within API Backlog list will be done in batch as part of M5.

**Additional comments**
<!-- Add any other comments here as needed. -->
