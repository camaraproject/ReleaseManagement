---
name: 💡 Fall25 M3 Review 🌟
about: Request the review of a Fall25 M3 release PR by the Release Mgmt team
title: '$repo name$ $releasenr$ (Fall25 M3) release review'
labels: 'Fall25 M3 review'
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
- [ ] changelog updated (structure in line with template, for public release all changes since last public release must be listed, Commonalities & ICM release candidates referred)
- [ ] readme updated (correct naming "pre-release" and release number, API versions naming, alignment with template) 
- [ ] API readiness checklist(s) (check link to Commonalities and ICM r3.2)
- [ ] API description (ensure that the API readiness checklists have been updated with the additional line for the API Description and contains the link to the current API descriptions)

Specific checks for alignment with Commonalities r3.2:
See Analysis here:  https://lf-camaraproject.atlassian.net/wiki/x/uoDIBg

- [ ] Remove the 401 AUTHENTICATION_REQUIRED code 
- [ ] Mandatory text on non-documented error responses
- [ ] remove IDENTIFIER_MISMATCH error and add DeviceResponse object (when Device object is used in the request)
- [ ] Mandatory text proposed when duration string format is used
- [ ] X-Correlator (header & parameter) referencing XCorrelator schema with updated string pattern 

For Subscription APIs:

- [ ] Update types property of SubscriptionRequest to allow more than one event type per subscription (optional)
- [ ] Update types property of SubscriptionRequest to use SubscriptionEventType schema (enum of defined types)
- [ ] 3.2 subscription-started event (optional event)
- [ ] 3.3 subscription-updated event (optional event)
- [ ] 3.4 subscription-ends --> subscription-ended (event name change)
- [ ] Add sink pattern and specific 400 - INVALID_SINK error

**Release actions**

Assign this issue to yourself or another RM team member and follow the below list. 
When done, tick the box in this issue (requires write access, leave a comment otherwise). 

- [ ] Short link to release review issue added to release trackers ("M3 #nnn")
- [ ] Review comments provided (on behalf of Release Management)
- [ ] Review comments addressed (by release PR editor)
- [ ] Release PR approved (on behalf of Release Management)
- [ ] PR merged (by API repository codeowner)
- [ ] Release created within GitHub (by API repository codeowner)
- [ ] Release Tracker updated (with creation date of the release and the release tag link)

(Note: for pre-releases there is no update needed of website and other places. For public releases within Fall25 M4 the updates of GitHub README, CAMARA website and within API Backlog list will be done in batch as part of M5 milestone.)

**Additional comments**
<!-- Add any other comments here as needed. -->
