# API release guidelines

- [Definitions](#definitions)
- [API releases - overview](#API-releases---overview)
- [Release guidelines](#Release-guidelines)
- [Releasing an API step by step](#Releasing-an-API-step-by-step)
- [Releasing an update of a public API version](#Releasing-an-update-of-a-public-API-version)
- [Example of the API release process](#Example-of-the-API-release-process)

## Definitions

| Term | Definition |
|------|-------|
| pre-release | A pre-release is a GitHub release of an API repository which contains alpha or release-candidate API versions (*). Note: the term release is also often used here but it should be clear from the context. |
| release | A release is a GitHub release of an API repository which contains public API versions - initial versions (0.y.z) or stable versions (x.y.z with x>=1) . Releases may be proposed as part of a meta-release.|
| meta-release | A meta-release is a set of public API versions across CAMARA, made available at a given point in time (Spring and Fall). All API versions of a given meta-release shall be aligned to the Commonalities and Identity and Consent Management (ICM) public releases included in that same meta-release.|
| maintenance release | A maintenance release is a Github release of a repository which contains a patch update of a public API version. |
| release tag | A release tag is a Git tag placed on the main or a maintenance branch that identifies a release of the API repository. It is created as part of a GitHub release |
| release package | A release package is a zip file of the GitHub repository created using the GitHub release mechanism. It contains a snapshot of the full API repository content which is marked with the release tag. |
| GitHub release | A GitHub release is the combination of a release tag and, optionally, a release package of the GitHub repository (zip file) created using the GitHub release feature. A GitHub release applies to the full API repository. A GitHub release may contain alpha, release-candidate or public API version(s). A GitHub release shall not include any wip API versions.`|
| release pull request (PR) | A release PR is created within an API repository to prepare its GitHub release. A release PR shall minimally set the version and URL fields in the API yaml file(s) to the exact API version and establish the availability of the API release assets as per the API readiness checklist. |
| API release tracker | An API release tracker provides the visibility on the progress of the (pre-)releases of a given API version within the CAMARA Wiki. For each API version planned for public release (as part of or outside a meta-release), its release tracker shall be created under their API Release Tracking page on the CAMARA Wiki. |

(*) NOTE: pre-releases are not meant to be included in a meta-release. All pre-releases are publicly available in the CAMARA GitHub and can be used AT THE USER'S OWN RISK, as changes may happen to such API versions without notice.

## API releases - overview

### Release process

To prepare the release of a public API version, API versions shall be (pre-)released as follows:

* before M3, release (optionally) one or more alpha API versions as needed
* to reach M3, release the first release-candidate API version:
  * the release-candidate implements the scope of the target public API version.
  * this pre-release is agreed to be ready for API implementation and functional testing.
  * it is aligned with the alpha release of Commonalities and ICM for the meta-release.
  * it includes all required API release assets as defined in the API Readiness Checklist for release candidiate API versions.
* between M3 and M4, release additional release-candidate API versions as needed
  * to fix bugs reported by the API users
  * to include updates needed to be in-line with the release candidiates of Commonalities and ICM (M2)
* to reach M4, release the public API version:
  * this is the API release for inclusion in the meta-release (if so planned).
  * the public API release must be aligned with the public releases of Commonalities and ICM (M4).
  * it includes all required API release assets as defined in the API Readiness Checklist for public API versions.

An API Sub Project or independent Sandbox team can release as many alpha and release-candidate API versions as useful for API development and testing. In between (pre-)releases, the API version shall be set to `wip` (to indicate that this API version should not be used).

### Public API versions

Public API versions can have an initial or stable status.

 * An initial public API version is the result of rapid development and can be
   * released and published at any time (outside the meta-release process) in order to allow for rapid evolution of APIs.
   * published as part of a meta-release, in which case, the milestones defined for the meta-release have to be followed. For more details see also: [Meta-release Process](https://lf-camaraproject.atlassian.net/wiki/x/Zwne).
* A public API version is released only if it provides all required API readiness checklist items (see: API Readiness Checklist section in the [API Release Process](https://lf-camaraproject.atlassian.net/wiki/x/jine).
* For stable public API versions, participation in the meta-release process is mandatory. As stable API versions are recommended for use in commercial applications, and the user can expect that subsequent public API versions will be backward-compatible, there are additional API readiness checklist items to be provided for the release of stable API versions.

### Meta-release

To be part of a meta-release, the API Sub Project or independent Sandbox team needs to participate in the meta-release process. For the meta-release, the following needs to be provided:

* the API release tracker (see [API release trackers](https://lf-camaraproject.atlassian.net/wiki/x/ZhHe))
* the expected (pre-)releases at the respective M3 and M4 milestones
* minimally an initial public API version
* the required set of API release assets according to the API readiness checklist (see below).

Once released as part of a meta-release, it is expected that a public API releases an update in the next meta-release to align with updated Commonalities and ICM guidelines.

## Release guidelines

### GitHub release 

Technically, a release of an API version consists in the GitHub release of the repository containing the API version. Creating it involves using standard GitHub capabilities as follows: 

* A GitHub issue defining the scope of the API version to be released
* A dedicated "release PR" (pull request) associated to this issue, setting the version and more (see below) 
* A GitHub release package (zip file of the whole API repository, including API(s) and release assets)
* A GitHub release tag with the release number `rx.y` following the API release numbering guidelines (see next section).

### API release numbering

---

**IMPORTANT: Release numbers are NOT related to the API version.**

* **API release numbers start at r1.1**

* API versioning is described in the API-design-guidelines.md available in the documentation folder of the [Commonalities working group](https://github.com/camaraproject/Commonalities), and on the [Release Management wiki](https://lf-camaraproject.atlassian.net/wiki/x/VA7e).

---

API release numbers are GitHub tags of the format `rx.y`.

The release numbers shall follow the guidelines described below.

* Release numbers start with x=1 and y=1: r1.1.
* y is incremented by 1 at each subsequent alpha, release-candidate and public release, and for a maintenance release, e.g. rx.y+1.
* After a meta-release of an API through release rx.y, the next release number for this API is rx+1.1 (y resets to 1).
* In case of maintenance of a release rx.y, the new public release shall be rx.y+1.

Example of continuous release numbering of an API's versions across its release types is given in the below table.

| Release type | API version | release tag | release package | release package label |
|------|------|:------:|:------:|:------:| 
| N/A | work-in-progress | N/A | N/A | N/A |
| pre-release | alpha | rx.1 ... rx.m | optional | `pre-release` |
| pre-release | release-candidate | rx.m+1 ... rx.n | mandatory | `pre-release` |
| release | public | rx.n+1 | mandatory | `latest` |
| maintenance release | public | rx.n+2 ... rx.n+p | mandatory | `latest` |

## Releasing an API step by step

This section lists the steps to release an API version. More details can be found here: [API Release Process](https://lf-camaraproject.atlassian.net/wiki/x/jine).

**Release preparation**

* Create a GitHub issue defining the scope of the targeted API version. Descriptive information in this issue can be reused in the `CHANGELOG.md` file in the release notes part.
* Create the API release tracker for the target API version as described here: [API release trackers](https://lf-camaraproject.atlassian.net/wiki/x/ZhHe).

**API version development**

On the main branch,
* develop the API scope in a "work-in-progress mode" (API version = `wip` and version in URL is `vwip`).
* make sure to create the required release assets and record them in the `APIname-API-Readiness-Checklist.md` file. If this file is not yet available, copy and rename the template `API-Readiness-Checklist.md` from the [ReleaseManagement](https://github.com/camaraproject/ReleaseManagement) / documentation folder, and prefix it with the API name.

**Create the release PR**

Once the defined scope and required stability is reached, create the (pre-)release PR.

A (pre-)release PR provides only the following changes: 
* update of the version information in the API OAS definition files (no `wip` in the version field and base URL of any of the API files).
* update all links (URLS) to point to resources of the release and include the release number on their path (no links with `main`, no relative links). 
* complete the `APIname-API-Readiness-Checklist.md` file ensuring all required release assets are available. If not yet available, copy the template `API-Readiness-Checklist.md` from the [ReleaseManagement](https://github.com/camaraproject/ReleaseManagement) / documentation folder, and prefix it with the API name.
* update the `CHANGELOG.md` file in the home of the API repository. If not yet available, copy the `CHANGELOG_TEMPLATE.md` from the [ReleaseManagement](https://github.com/camaraproject/ReleaseManagement) / documentation folder (removing the `_TEMPLATE` part). See also the example available in the documentation / SupportingDocuments / `CHANGELOG_EXAMPLE.md`.
  * add a new section at the top of your `CHANGELOG.md` file for the release and each API version with content as follows: 
    * for an alpha release, the delta with respect to the previous release
    * for the first release-candidate, all changes since the last public release
    * for subsequent release-candidate(s), only the delta to the previous release-candidate
    * for a public release, the consolidated changes since the previous public release
* update of the API repository `README.md` file (as necessary)
* request the review of the release PR by adding the camaraproject/release-management_maintainers to the list of reviewers of the release PR. 

**Create the release**
* check the progress of the release PR approval in the review issue created by the Release Management team
* merge the approved release PR
* create the release:
  * an API release is created using the GitHub release feature (a release tag and, optionally, a release package).
  * the release name shall be the same as the release tag and shall have the following format: `rx.y`
  * the x.y number shall follow the release numbering scheme  as defined in the above section on API release numbering
  * the release description within the GitHub release should be a copy of the section about the release within the CHANGELOG.md
* update the API release tracker with the date and release tag link for the release

## Releasing an update of a public API version

### MAJOR or MINOR update

For MAJOR and MINOR updates of a public API version x.y.z (released as rm.n), follow the above API version release process (see "Releasing an API step by step"), increasing the x (MAJOR) or y (MINOR) version number by 1 respectively, and starting the release numbering at rm+1.1. A new API release tracker shall be created for the new API version.

### PATCH update (maintenance release)

In case a PATCH update of a public API version x.y.z (released as rm.n) is required, the patched public API version x.y.z+1 shall be released as a maintenance release rm.n+1 on a separate branch referred to as a maintenance branch. 

The name of the maintenance branch shall be `maintenance-rm` (for a patch of an API publicly released as rm.n). Any further patches to that API version shall be done on this same branch. 

Preferably, a maintenance release shall be merged into the main branch as soon as possible if the patch is applicable to the main branch.

The maintenance release shall replace the public API release, and its API release tracker shall be updated. This implies to update the API release tracker (page) name with the patch version and adding the release tag link and the date of its publication.

NOTE: a patch is the only case for which a separate branch is created and maintained within the API repository (as pull requests should be prepared within forks of the API repository, c.f. [Governance](https://github.com/camaraproject/Governance) / `CONTRIBUTING.md`

## Example of the API release process

To release a MINOR update of a public API version 1.0.0, resulting in the release of public API version 1.1.0:

* Develop the 1.1.0 updates on the main branch. The first PR shall update the OAS file setting the API version to `wip`, and the URL to `vwip`.
* Once sufficiently stable, create a release PR for the API version 1.1.0-alpha.1.
* After release PR approval, create the pre-release rx.1 and publish it on the API release tracker.
* Additional alpha API versions 1.1.0-alpha.p may be released. For each such alpha API version, set the API version to `wip` in the first API update PR, and only set the next API version in the release PR of the next pre-release. The alpha number evolves with each following pre-release numbered rx.2 - rx.m.
* When the API version scope development is complete, create a release PR for the release-candidate API version 1.1.0-rc.1
* Additional release-candidate API versions 1.1.0-rc.q may be released. For each such release-candidate API version, set the API version to `wip` in the first API update PR, and only set the next API version in the release PR of the next pre-release. The rc number evolves with each following pre-release numbered rx.m+1 - rx.n.
* When the API version is ready for public release, create the release PR that sets the public API version to 1.1.0. (this PR minimally removes the rc extensions from the version and URL fields in the API yaml file and assures all API release assets are available as per the API readiness checklist).
* After release PR approval, create the release rx.n+1 for the public API version 1.1.0 and update the API release tracker.
* The approved public API version 1.1.0 will be included in the meta-release.
* If a patch is provided for the released API, it shall be declared as the latest release, and the information shall be published on the existing API release tracker.
