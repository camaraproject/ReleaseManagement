# API release guidelines

## Definitions

| Term | Definition |
|------|-------|
| release | The release of an API version consists in the creation of a GitHub release of the API's repository, with a release tag and (optionally for alpha) a release package. A release can be created for any alpha, release-candidate or public-release API version. No releases can be created for wip API versions.|
| pre-release | The term pre-release is used to refer to the release of any of the alpha or release-candidate API versions (*) |
| alpha-release | The term alpha-release is used to refer to the release of an alpha API version. |
| release-candidate | The term release-candidate is used to refer to the release of a release-candidate API version. |
| public-release | The term public-release is used to refer to the release of a public-release API version. It can have the status initial or stable.|
| meta-release | A meta-release is a set of public-releases of API versions made available at a given point in time (Spring and Fall). All API versions of a given meta-release shall be aligned to the Commonalities and Identity and Consent Management (ICM) public-releases included in that same meta-release.|
| maintenance-release | The term maintenance-release is used to refer to a patch update of a public-release API version. |
| release tag | A release tag is a GitHub tag placed on the main or a maintenance branch that identifies a release of the API version's repository.|
| release package | A release package is a zip file of the repository created using the GitHub release mechanism together with the release tag. It contains a snapshot of the full API Sub Project repository with the content indicated by the release tag.
| API release tracker | An API release tracker is a page that provides the visibility on the progress of the release of a given API version. All API versions released by an API Sub Project shall have a tracker under their API Sub Project's API Release Tracking page. |

(*) NOTE: all pre-releases are publicly available in the CAMARA GitHub and can be used AT THE USER'S OWN RISK, as changes may happen to such API versions without notice.

## API releases

In preparation of the public-release of an API version, an API Sub Project can create as many alpha and release-candidate API versions as needed for API development and testing. The API versioning is done as described in the API design guidelines (section on versioning). 

The API Sub Project creates a release for an API version as follows:

* a pre-release may be created for an alpha API version.
* a pre-release must be created for each release-candidate API version.
* a public-release must be created for the an API version in order to be published as part of a meta-release.

Public-releases can have an initial or stable status:

* an initial public-release indicates that the public-release API version is the result of rapid development and is still unstable, e.g. API versions with a v0.x.y version number.
* a stable public-release indicates that the public-release API version is stable and will be maintained.

When planning to deliver a public-release API version into a meta-release, the API Sub Project needs to participate in the meta-release cycle as described below. For more details see also: [Meta-release Process](https://wiki.camaraproject.org/x/G7N3).

To be part of a meta-release, (pre-)releases need to be provided as follows:

* the expected (pre-)releases for alpha, release-candidate and public-release API versions need to be provided.
* minimally an initial public-release need to be provided for the meta-release.
* each (pre-)release must include the required set of API release assets according to the API readiness checklist described below.
* API (pre-)releases are numbered (tagged) using the API release numbering guideline (see below).

Technically, an API release is created using GitHub features:

* A GitHub issue for the release
* A "release PR" associated to this issue
* A GitHub release package (zip file of the API Sub Project repository)
* A GitHub release tag with the release name rx.y

## API release numbering

---

**IMPORTANT: Release numbers are not related to the API version.**

---

API release numbers are GitHub tags of the format "rx.y".

The release numbers shall follow the guidelines described below.

* Release numbers start with x=1 and y=1: r1.1.
* y is incremented by 1 at each subsequent alpha, release-candidate and public-release, and for a maintenance release, e.g. rx.y+1.
* After a meta-release of an API through release rx.y, the next release number for this API is rx+1.1 (y resets to 1).
* In case of maintenance of a release rx.y, the new public-release shall be rx.y+1.

Example of continuous release numbering of an API version across its release types.

| API version | release tag | release package | release package tag |
|------|:------:|:------:|:------:| 
| work-in-progress | N/A | N/A| N/A |
| alpha | rx.1 ... rx.m | optional | optional [ "pre-release" ] |
| release-candidate | rx.m+1 ... rx.n | mandatory | "pre-release" |
| public-release | rx.n+1 | mandatory | "latest" |
| maintenance-release | rx.n+2 ... rx.n+p | mandatory | "latest" |

## How to create an API release ? 

An API release is created using the GitHub PR and release features and results in:

* a **release tag** (following the release numbering guidelines below) on the main or on a maintenance release branch, identifying the release of the API version.
* a **release package** containing the API's repository with the corresponding API release assets for the released API version (zip file). This is optional for alpha releases.

API releases are numbered (tagged) following the API release numbering guidelines (see section above).

## Releasing an API step by step

This section gives the overview of the steps to release an API. More details can be found in the [API Release Process](https://wiki.camaraproject.org/x/AgAVAQ) description.

**Release preparation**

* Create a GitHub issue defining the scope of the targeted API release. Descriptive information in this issue can be reused in the changelog/release notes.
* Create the API release tracker for the target API version as describer here: [API release tracking process](https://wiki.camaraproject.org/x/HQBFAQ).

**Release development**

* On the main branch, develop the API scope in a "work-in-progress mode" (API version = wip and version in URL is vwip).
  * during development and test, make sure to create and record the required release assets according to the [API-Readiness-Checklist.md]() file
* Once the required stability is reached, create the "release PR". The “release PR” provides only the following changes: 
  * update the version information in the API OAS definition files (no "wip" in any of the API files).
  * update of the local copy of the [API-Readiness-Checklist.md]() ensuring all required release assets are available.
  * update of the [Changelog.md]() in the repository with new content on the top for each changed API:
    * for an alpha API version, the delta to the previous release
    * for the first release-candidate, all changes since the last public-release
    * for the subsequent release-candidate, only the delta to the previous release candidate
    * for the public-release, the consolidated changes since the last public-release
  * the update of the [README.md]() (as necessary)  *

* Manage the "release PR" approval, merge the approved "release PR" and create the release
  * An API release is created using the GitHub release feature.
  * The release name shall be the same as the release tag and shall have the following format: rx.y
  * The x.y number shall follow the release numbering scheme  as defined in the above section on API release numbering
  * Outside the API Sub Project, the release name shall be the API name (for definition see the versioning section in the [API Design Guidelines](https://github.com/camaraproject/Commonalities/blob/main/documentation/API-design-guidelines.md)) followed by the release number e.g. qod rx.y

**Release process**

Repeat the above release steps for

* alpha releases up to the M3 milestone (at M3 the first release-candidate shall be ready)
* release-candidates between the M3 and the M4 milestone,
* finishing with the public-release for inclusion in the meta-release at the M5 milestone

**Release patch**

In case an update of a public-release API version x.y.z is required, the patched public-release API version x.y.z+1 shall be created through a maintenance-release on a separate branch referred to as a maintenance branch. 

NOTE: a patch is the only case for which a separate branch is created and maintained.
