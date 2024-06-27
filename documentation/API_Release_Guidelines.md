# API release guidelines

## Definitions

| Term | Definition |
|------|-------|
| pre-release | A pre-release is a GitHub release of an alpha or release-candidate API versions. Note: the term release is also often used here but should be clear from the context. (*) |
| release | A release is a GitHub release of a public API version. Releases may be proposed as part of a meta-release.|
| release of an initial public API version | Initial public API versions only exists for new APIs. It concerns public APIs versions with x = 0 (0.y.z without version extension). |
| release of a stable public API version | A stable public API version concerns an API version together with all required release assets. They are included in a meta-release. Stable public API versions are recommended for use in commercial applications.  |
| meta-release | A meta-release is a set of public API versions made available at a given point in time (Spring and Fall). All API versions of a given meta-release shall be aligned to the Commonalities and Identity and Consent Management (ICM) public releases included in that same meta-release.|
| maintenance release | A maintenance release is the release of a patch update of a public API version. |
| release tag | A release tag is a GitHub tag placed on the main or a maintenance branch that identifies a release of the API version's repository.|
| release package | A release package is a zip file of the GitHub repository created using the GitHub release mechanism. It contains a snapshot of the full API version repository marked with the release tag. |
| GitHub release | A GitHub release is the combination of a release tag and, optionally, a release package of the GitHub repository (zip file) created using the GitHub release feature. A GitHub release applies to the full API repository. A GitHub release may containing any alpha, release-candidate or public API version(s). A GitHub release shall not include any wip API versions.`|
| release PR | A release PR is created for an API version to prepare its GitHub release. A release PR shall minimally set the version fields in the API yaml file to the exact API version and establish the availability of the API release assets as per the API readiness checklist. |
| API release tracker | An API release tracker provides the visibility on the progress of the (pre-)releases of a given API version. Each API version planned for release by an API Sub Project shall have its tracker under their API Sub Project's API Release Tracking page. |

(*) NOTE: pre-releases are not meant to be included in a meta-release. All pre-releases are publicly available in the CAMARA GitHub and can be used AT THE USER'S OWN RISK, as changes may happen to such API versions without notice.

## API releases - overview

To prepare the release of a public API version, at least two intermediate API versions must be (pre-)released as follows:

* at M3: the release-candidate API version implementing the defined API scope for the release (achieved through one or more alpha releases), agreed stable for implementation and functional testing and aligned with the release-candidate versions of Commonalities and ICM (M1).
* at M4: the public API version ready for the meta-release, aligned with the public versions of Commonalities and ICM (M2).

An API Sub Project can create as many wip, alpha and release-candidate API versions as needed for API development and testing.

The API Sub Project shall create a release for an API version as follows:

* a pre-release may be created for any alpha API version. 
* a pre-release must be created for each release-candidate API version.
* a release must be created for each public API version.

To (pre-)release an API version a release PR needs to be created:

* Before M3 or M4, the release PR is prepared. It shall provide all release assets as per the API readiness checklist.
* Once the release PR is approved, the corresponding GitHub release is created and M3/M4 is declared.

Inclusion in the meta-release is done by updating the API release tracker with the M3/M4 date and release tag links 

A subsequent release of an API version is done if/when there are updates to the API. All updates shall be recorded in the Changelog.md file


Public API versions can have an initial or stable status:

 * An initial public API version is the result of rapid development and can be
   * released and published at any time (outside the meta-release process) in order to allow for rapid evolution of APIs.
   * published as part of a meta-release. In this case, the milestones defined for the meta-release have to be followed. For more details see also: [Meta-release Process](https://wiki.camaraproject.org/x/G7N3).
 * An API version is released only if it provides all required API readiness checklist items (see: [API Readiness Checklist](https://wiki.camaraproject.org/display/CAM/API+Release+Process#APIReleaseProcess-APIreadinesschecklist).
* Stable public API versions are recommended for use in commercial applications. The user can expect that subsequent public API versions will be backward-compatible with the one they are using, unless explicitly announced otherwise.

To be part of a meta-release, (pre-)releases need to be provided as follows:

* the expected (pre-)releases for alpha, release-candidate and public API versions need to be provided at the respective M3, M4 and M5 milestones
* minimally an initial public release needs to be provided for the meta-release.
* each (pre-)release must include the required set of API release assets according to the API readiness checklist described below.
* API (pre-)releases are numbered (tagged) using the API release numbering guideline (see below).

## What is an API release ? 

Technically, an API release is created using the GitHub issues, PR and release features and requires:

* A GitHub issue defining the scope of the release of teh API version
* A release PR associated to this issue (setting the version) and more - see below)
* A GitHub release package (zip file of the whole API repository, including API(s) and release assets)
* A GitHub release tag with the release number "rx.y" following the API release numbering guidelines (see next section).

## API release numbering

---

**IMPORTANT: Release numbers are NOT related to the API version.**

* **API release numbers start at r1.1**

* API versioning is described in the Commonalities [API-desighn-guidelines.md](https://github.com/camaraproject/Commonalities/blob/main/documentation/API-design-guidelines.md) and on the [Release Management wiki](https://wiki.camaraproject.org/x/a4BaAQ).

---

API release numbers are GitHub tags of the format "rx.y".

The release numbers shall follow the guidelines described below.

* Release numbers start with x=1 and y=1: r1.1.
* y is incremented by 1 at each subsequent alpha, release-candidate and public release, and for a maintenance release, e.g. rx.y+1.
* After a meta-release of an API through release rx.y, the next release number for this API is rx+1.1 (y resets to 1).
* In case of maintenance of a release rx.y, the new public release shall be rx.y+1.

Example of continuous release numbering of an API version across its release types.

| Release type | API version | release tag | release package | release package tag |
|------|------|:------:|:------:|:------:| 
| N/A | work-in-progress | N/A | N/A | N/A |
| pre-release | alpha | rx.1 ... rx.m | optional | optional: "pre-release" |
| pre-release | release-candidate | rx.m+1 ... rx.n | mandatory | "pre-release" |
| release | public | rx.n+1 | mandatory | "latest" |
| maintenance release | public | rx.n+2 ... rx.n+p | mandatory | "latest" |

## Releasing an API step by step

This section gives the overview of the steps to release an API. More details can be found here: [API Release Process](https://wiki.camaraproject.org/x/AgAVAQ).

**Release preparation**

* Create a GitHub issue defining the scope of the targeted API release. Descriptive information in this issue can be reused in the changelog/release notes.
* Create the API release tracker for the target API version as describer here: [API release trackers](https://wiki.camaraproject.org/x/HQBFAQ).

**Release development**

* On the main branch,
  * develop the API scope in a "work-in-progress mode" (API version = wip and version in URL is vwip).
  * make sure to create the required release assets and record them in the [API-Readiness-Checklist.md]() file
* Once the required stability is reached, create the "release PR". The “release PR” provides only the following changes: 
  * update of the version information in the API OAS definition files (no "wip" in any of the API files).
  * update your [<API Sub Project name>-API-Readiness-Checklist.md]() ensuring all required release assets are available. If not yet available, create a local copy under the /documentation folder and prefix it with your API Sub Project name (Copy from [ReleaseManagement/documentation/API-Readiness-Checklist.md](https://github.com/camaraproject/ReleaseManagement/blob/main/documentation/API-Readiness-Checklist.md).
  * update your [CHANGELOG.md]() in the home of the repository. Add a new section at the top for each API version with the following content:
    * for an alpha API version, the delta to the previous release
    * for the first release candidate, all changes since the last public release
    * for the subsequent release candidate, only the delta to the previous release candidate
    * for the public release, the consolidated changes since the last public release
  * update of the [README.md]() (as necessary)  *

* Manage the "release PR" approval, merge the approved "release PR" and create the release
  * An API release is created using the GitHub release feature.
  * The release name shall be the same as the release tag and shall have the following format: rx.y
  * The x.y number shall follow the release numbering scheme  as defined in the above section on API release numbering
  * Outside the API Sub Project, the release name shall be referred to with the API name (for definition see the versioning section in the [API Design Guidelines](https://github.com/camaraproject/Commonalities/blob/main/documentation/API-design-guidelines.md)) followed by the release number e.g. quality-on-demand rx.y

**Release process**

Repeat the above release development steps for

* alpha releases before M3; the first release candidate is created for M3
* release candidates between M3 and M4
* the public release for M4

**Release maintenance**

In case a patch update of a public API version x.y.z is required, the patched public API version x.y.z+1 shall be created as a maintenance release on a separate branch referred to as a maintenance branch. 

NOTE: a patch is the only case for which a separate branch is created and maintained within the API repository (as pull requests should be prepared within forks of the API repository, c.f. [Governance/CONTRIBUTING.md](https://github.com/camaraproject/Governance/blob/main/CONTRIBUTING.md))

**Example of the API release process**

To release a MINOR update of a publicly released API version 1.0.0, resulting in a the public release of API version 1.1.0:

* Develop the 1.1.0 update on the main branch. The first PR updates the version to wip, and the URL to contain vwip.
* Once sufficiently stable, create an alpha release PR that sets the API version to 1.1.0-alpha.1 and will create release rx.1.
* Several alpha API versions may be released, each setting the API version back to "wip" in the first API update PR (rx.2 - rx.m)
* Then (at least) one (or more) release-candidate API versions may be created and released (rx.m+1 - rx.n) 
* The last release-candidate API version will be proposed for public release. 
* For meta-release approval, create the public release PR for the next public API version 1.1.0.
* After meta-release approval, create the release for the new public API version 1.1.0, with its release tag rx.n+1 and release package ("latest")).