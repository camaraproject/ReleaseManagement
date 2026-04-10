<a href="https://github.com/camaraproject/ReleaseManagement/commits/" title="Last Commit"><img src="https://img.shields.io/github/last-commit/camaraproject/ReleaseManagement?style=plastic"></a>
<a href="https://github.com/camaraproject/ReleaseManagement/issues" title="Open Issues"><img src="https://img.shields.io/github/issues/camaraproject/ReleaseManagement?style=plastic"></a>
<a href="https://github.com/camaraproject/ReleaseManagement/pulls" title="Open Pull Requests"><img src="https://img.shields.io/github/issues-pr/camaraproject/ReleaseManagement?style=plastic"></a>
<a href="https://github.com/camaraproject/ReleaseManagement/graphs/contributors" title="Contributors"><img src="https://img.shields.io/github/contributors/camaraproject/ReleaseManagement?style=plastic"></a>
<a href="https://github.com/camaraproject/ReleaseManagement" title="Repo Size"><img src="https://img.shields.io/github/repo-size/camaraproject/ReleaseManagement?style=plastic"></a>
<a href="https://github.com/camaraproject/ReleaseManagement/blob/main/LICENSE" title="License"><img src="https://img.shields.io/badge/License-Apache%202.0-green.svg?style=plastic"></a>
<img src="https://img.shields.io/badge/Working%20Group-red">

# Release Management
Repository to describe, develop, document and test the Release Management process.

## Scope
* Guidelines and artefacts for Release Management in CAMARA
* Describe, develop, document and apply the deliverables
* Started: November 2023

## Introduction

The Release Management documentation describes 

- the automated API release process
- the CAMARA meta-release process
- the Commonalities and ICM release process
- the API versioning guidelines (input to Commonalities)
- the artifacts enabling the automatied API release process

NOTE: the automation process also leverages support from the `project-administration` and the `tooling` repositories. 

## API Release Process

API Release Process documentation and artifacts are located in the [**`documentation`**](documentation/README.md) folder of the Release Management repository:
   - [**CAMARA Release Process Documentation**](documentation/README.md) - the main entry point for automated release process documentation.
   - [API Readiness Checklist](/documentation/readiness/api-readiness-checklist.md) - the checklist that defines release readiness of the API according to its terget release status (alpha, release-candidate, public).
   - For the reference documentation on API versioning, please see "Versioning" section in the CAMARA API Design Guidelines document in [Commonalities](https://github.com/camaraproject/Commonalities).

## Release Management Wiki

Beyond the above reference release management documentation in GitHub, additional information is available on the [Release Management wiki](https://lf-camaraproject.atlassian.net/wiki/x/VA7e). In particular, you can find there information about:

* **Meta-release process**

  * [Meta-releases](https://lf-camaraproject.atlassian.net/wiki/x/bmTe) - list of ongoing and past meta-releases, their contained APIs and their associated Commonalities and ICM releases.
  * [Meta-release Process](https://lf-camaraproject.atlassian.net/wiki/x/Zwne) - the meta-release milestone description and their related activities and time-line.

* **Commonalities and ICM release process**
  * [Commonalities and ICM Release Process](https://lf-camaraproject.atlassian.net/wiki/spaces/CAM/pages/14551399/Meta-release+Process#Commonalities-and-ICM) - more information about processes and release numbering for Commonalities and ICM releases. 

## Release Management repository

The [CHANGELOG.md](/CHANGELOG.md) file provides the CHANGELOG history between releases of the Release Management repository. 

The automated release process has been introduced with the Spring26 meta-release.

## Contributing
* Meetings are held virtually
  * Schedule: Weekly on Tuesday's at 08:00 PT / 16:00 UTC / 17:00 CET
  * Meeting link: [Meeting Registration / Join](https://zoom-lfx.platform.linuxfoundation.org/meeting/97762557636?password=e5f98402-8c29-448d-a8b1-f2dceaa9d4ba)
  * Meeting minutes are available within the [wiki of the Release Management Working Group](https://lf-camaraproject.atlassian.net/wiki/x/VA7e)
* Mailing List
  * Subscribe / Unsubscribe to the mailing list of this Working Group <https://lists.camaraproject.org/g/wg-release-management>.
  * A message to all Contributors of this Working Group can be sent using <wg-release-management@lists.camaraproject.org>.
