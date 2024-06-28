# API release guidelines

## Definitions

| Term | Definition |
|------|-------|
| pre-release | A pre-release is a GitHub release of an alpha or release-candidate API version. Note: the term release is also often used here but it should be clear from the context. (*) |
| release | A release is a GitHub release of a public API version. Releases may be proposed as part of a meta-release.|
| release of an initial public API version | Initial public API versions only exist for new APIs. It concerns public APIs versions with x = 0 (0.y.z without version extension). |
| release of a stable public API version | Stable public API versions are recommended for use in commercial applications. The user can expect that subsequent public API versions will be backward-compatible with the one they are using, unless explicitly announced otherwise.  |
| meta-release | A meta-release is a set of public API versions made available at a given point in time (Spring and Fall). All API versions of a given meta-release shall be aligned to the Commonalities and Identity and Consent Management (ICM) public releases included in that same meta-release.|
| maintenance release | A maintenance release is the release of a patch update of a public API version. |
| release tag | A release tag is a GitHub tag placed on the main or a maintenance branch that identifies a release in the API's repository.|
| release package | A release package is a zip file of the GitHub repository created using the GitHub release mechanism. It contains a snapshot of the full API repository marked with the release tag. |
| GitHub release | A GitHub release is the combination of a release tag and, optionally, a release package of the GitHub repository (zip file) created using the GitHub release feature. A GitHub release applies to the full API repository. A GitHub release may containing any alpha, release-candidate or public API version(s). A GitHub release shall not include any wip API versions.`|
| release PR | A release PR is created for an API version to prepare its GitHub release. A release PR shall minimally set the version and URL fields in the API yaml file to the exact API version and establish the availability of the API release assets as per the API readiness checklist. |
| API release tracker | An API release tracker provides the visibility on the progress of the (pre-)releases of a given API version. Each public API version planned for release by an API Sub Project shall have its release tracker under their API Sub Project's API Release Tracking page. |

(*) NOTE: pre-releases are not meant to be included in a meta-release. All pre-releases are publicly available in the CAMARA GitHub and can be used AT THE USER'S OWN RISK, as changes may happen to such API versions without notice.

## API releases - overview

### Release process

To prepare the release of a public API version, API versions shall be (pre-)released as follows:

* before M3, release one or more alpha API versions as needed
* to reach M3, release the first release-candidate API version:
  * the release-candidate implements the scope of the target public API version.
  * this pre-release is agreed as ready for API implementation and functional testing.
  * it is aligned with the release-candidate versions of Commonalities and ICM (M1).
* between M3 and M4, release one or more release-candidate API versions as needed
* to reach M4, release the public API version:
  * this is the version ready for inclusion in the meta-release (if so planned).
  * the public API version is aligned with the public versions of Commonalities and ICM (M2).

An API Sub Project can release as many alpha and release-candidate API versions as useful for API development and testing. In between releases, the API version is set to "wip" (to indicate that this API version should not be used).

### Public API versions

Public API versions can have an initial or stable status.

 * An initial public API version is the result of rapid development and can be
   * released and published at any time (outside the meta-release process) in order to allow for rapid evolution of APIs.
   * published as part of a meta-release. In this case, the milestones defined for the meta-release have to be followed. For more details see also: [Meta-release Process](https://wiki.camaraproject.org/x/G7N3).
 * A public API version is released only if it provides all required API readiness checklist items (see: [API Readiness Checklist](https://wiki.camaraproject.org/display/CAM/API+Release+Process#APIReleaseProcess-APIreadinesschecklist).
* Stable public API versions are recommended for use in commercial applications. The user can expect that subsequent public API versions will be backward-compatible with the one they are using, unless explicitly announced otherwise.

### Meta-release

To be part of a meta-release, the API Sub Project needs to participate in the meta-release process. For the meta-release, the following needs to be provided:

* the API release tracker (see [API release trackers](https://wiki.camaraproject.org/x/HQBFAQ))
* the expected (pre-)releases at the respective M3 and M4 milestones
* minimally an initial public API version
* the required set of API release assets according to the API readiness checklist (see below).

## Release guidelines

### GitHub release 

Technically, an API release is created using the GitHub issues, PR and release features and requires:

* A GitHub issue defining the scope of the release of the API version
* A release PR associated to this issue (setting the version) and more - see below)
* A GitHub release package (zip file of the whole API repository, including API(s) and release assets)
* A GitHub release tag with the release number "rx.y" following the API release numbering guidelines (see next section).

### API release numbering

---

**IMPORTANT: Release numbers are NOT related to the API version.**

* **API release numbers start at r1.1**

* API versioning is described in the Commonalities [API-design-guidelines.md](https://github.com/camaraproject/Commonalities/blob/main/documentation/API-design-guidelines.md) and on the [Release Management wiki](https://wiki.camaraproject.org/x/a4BaAQ).

---

API release numbers are GitHub tags of the format "rx.y".

The release numbers shall follow the guidelines described below.

* Release numbers start with x=1 and y=1: r1.1.
* y is incremented by 1 at each subsequent alpha, release-candidate and public release, and for a maintenance release, e.g. rx.y+1.
* After a meta-release of an API through release rx.y, the next release number for this API is rx+1.1 (y resets to 1).
* In case of maintenance of a release rx.y, the new public release shall be rx.y+1.

Example of continuous release numbering of an API version across its release types.

| Release type | API version | release tag | release package | release package label |
|------|------|:------:|:------:|:------:| 
| N/A | work-in-progress | N/A | N/A | N/A |
| pre-release | alpha | rx.1 ... rx.m | optional | optional: "pre-release" |
| pre-release | release-candidate | rx.m+1 ... rx.n | mandatory | "pre-release" |
| release | public | rx.n+1 | mandatory | "latest" |
| maintenance release | public | rx.n+2 ... rx.n+p | mandatory | "latest" |

## Releasing an API step by step

This section lists the steps to release an API version. More details can be found here: [API Release Process](https://wiki.camaraproject.org/x/AgAVAQ).

**Release preparation**

* Create a GitHub issue defining the scope of the targeted API version. Descriptive information in this issue can be reused in the changelog/release notes.
* Create the API release tracker for the target API version as describer here: [API release trackers](https://wiki.camaraproject.org/x/HQBFAQ).

**API version development**

On the main branch,
* develop the API scope in a "work-in-progress mode" (API version = wip and version in URL is vwip).
* make sure to create the required release assets and record them in the [API-Readiness-Checklist.md]() file

**Create the release PR**

Once the required stability is reached, create the release PR.

A release PR provides only the following changes: 
* update of the version information in the API OAS definition files (no "wip" in the version field or URL of any of the API files).
* update the [API-Readiness-Checklist.md]() ensuring all required release assets are available. If not yet available, create a local copy under the /documentation folder and prefix it with your API Sub Project name (Copy from [ReleaseManagement/documentation/API-Readiness-Checklist.md](https://github.com/camaraproject/ReleaseManagement/blob/main/documentation/API-Readiness-Checklist.md).
* update the [CHANGELOG.md]() in the home of the API repository. If not yet available, copy from [ReleaseManagement/documentation/CHANGELOG_TEMPLATE.md](https://github.com/camaraproject/ReleaseManagement/blob/main/documentation/CHANGELOG_TEMPLATE.md). See also the example available there.
  * add a new section at the top for the release and each API version with the following content:
    * for each first alpha or release-candidate API version, all changes since the release of the previous public API version
    * for subsequent alpha or release-candidate API versions, the delta with respect to the previous pre-release
    * for a public API version, the consolidated changes since the release of the previous public API version
* update of the [README.md]() (as necessary)

**Create the release**
* manage the release PR approval
* merge the approved release PR
* create the release:
  * an API release is created using the GitHub release feature (a release tag and, optionally, a release package).
  * the release name shall be the same as the release tag and shall have the following format: rx.y
  * the x.y number shall follow the release numbering scheme  as defined in the above section on API release numbering
  * note: outside the API Sub Project, the release name shall be referred to with the API name (for definition see the versioning section in the [API Design Guidelines](https://github.com/camaraproject/Commonalities/blob/main/documentation/API-design-guidelines.md)) followed by the release number e.g. quality-on-demand rx.y
* update the API release tracker with the date and release tag link for the release

**Maintenance release**

In case a patch update of a public API version x.y.z is required, the patched public API version x.y.z+1 shall be created through a maintenance release on a separate branch referred to as a maintenance branch. 

NOTE: a patch is the only case for which a separate branch is created and maintained within the API repository (as pull requests should be prepared within forks of the API repository, c.f. [Governance/CONTRIBUTING.md](https://github.com/camaraproject/Governance/blob/main/CONTRIBUTING.md))

## Example of the API release process

To release a MINOR update of a public API version 1.0.0, resulting in the release of public API version 1.1.0:

* Develop the 1.1.0 updates on the main branch. The first PR shall update the OAS file setting the API version to wip, and the URL to vwip.
* Once sufficiently stable, create a release PR for the API version 1.1.0-alpha.1.
* After release PR approval, create the pre-release rx.1 and publish it on the API release tracker.
* Several alpha API versions 1.1.0-alpha.p may be released, each setting the API version back to "wip" in the first API update PR and evolving the alpha number with each following pre-release (rx.2 - rx.m).
* When the API version is ready, create a release PR for the API version 1.1.0-rc.1
* Several release-candidate API versions 1.1.0-rc.q may be released, each setting the API version back to "wip" in the first API update PR and evolving the rc number with each following pre-release (rx.m+1 - rx.n).
* When the API version is ready for public release, create the release PR that sets the public API version to 1.1.0. (this PR minimally removes the rc extensions from the version and URL fields in the API yaml file and assures all API release assets are available as per the API readiness checklist).
* After release PR approval, create the release rx.n+1 and publish it on the API release tracker.
* The approved public API version 1.1.0 will be included in the meta-release as planned.
