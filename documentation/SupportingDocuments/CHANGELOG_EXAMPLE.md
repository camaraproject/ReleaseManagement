# Changelog QualityOnDemand

NOTE: As this **example CHANGELOG file** is based on the actual CHANGELOG of QualityOnDemand it is important to note that the content of the the v0.10.x releases is here **rewritten only for illustration purposes** according to the new release process. Within the real sub project the new release process will only be applied to new releases, the existing content of the CHANGELOG file SHALL NOT be rewritten!

## Table of contents

- **[r1.5 - patch](#r15---patch)**
- [r1.4 - public](#r14---public)
- [r1.3 - rc](#r13---rc)
- [r1.2 - rc](#r12---rc)
- [r1.1 - alpha](#r11---alpha)
- [v0.9.0](#v090)
- ...

**Please be aware that the project will have frequent updates to the main branch. There are no compatibility guarantees associated with code in any branch, including main, until it has been released. For example, changes may be reverted before a release is published. For the best results, use the latest published release.**

The below sections record the changes for each API version in each (pre-)release as follows:

* for the first alpha or release-candidate API version, all changes since the release of the previous public API version
* for subsequent alpha or release-candidate API versions, the delta with respect to the previous pre-release
* for a public API version, the consolidated changes since the release of the previous public API version

DISCLAIMER: in this example file, links and other content have been edited from the original to fit the example (hence links may be broken).

# r1.5 - patch

## Release Notes

This release contains the definition and documentation of
* quality-on-demand v0.10.1, a patch release of v0.10.0

The API definition(s) are based on
* Commonalities v0.2.0
* Identity and Consent Management v0.1.0

<!--In case of a repository with multiple APIs, list all APIs above, and for each API version that changed in this release, create a section as below, with the header 2: API-name API-version-x.y.z, and level 3 subsections. Also mention if an API in the repository is unchanged.-->

## quality-on-demand v0.10.1

**quality-on-demand v0.10.1 is a patch version. Please read also the notes and changes for v0.10.0 in r1.4**

- API definition **with inline documentation**:
  - [View it on ReDoc](https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/camaraproject/QualityOnDemand/r1.5/code/API_definitions/qod-api.yaml&nocors)
  - [View it on Swagger Editor](https://editor.swagger.io/?url=https://raw.githubusercontent.com/camaraproject/QualityOnDemand/r1.5/code/API_definitions/qod-api.yaml)
  - OpenAPI [YAML spec file](https://github.com/camaraproject/QualityOnDemand/blob/r1.5/code/API_definitions/qod-api.yaml)

### Fixed
 
* Updated the documentation to address the lack of `statusInfo` in `SessionInfo` temporary by @hdamker in https://github.com/camaraproject/QualityOnDemand/pull/269
  * Note: The parameter `statusInfo` will be added to `SessionInfo` within next regular release
* Fixed maximum duration in session info and improved documentation by @emil-cheung in https://github.com/camaraproject/QualityOnDemand/pull/277
  * Improved the documentation of "Extend the duration of an active session"
  * Improved the datatype "SessionInfo" to remove the maximum limit of duration

**Full Changelog**: https://github.com/camaraproject/QualityOnDemand/compare/r1.4...r1.5

# r1.4 - public

## Release Notes

This release contains the definition and documentation of
* quality-on-demand v0.10.0

The API definition(s) are based on
* Commonalities v0.2.0
* Identity and Consent Management v0.1.0

## quality-on-demand v0.10.0

**quality-on-demand v0.10.0 is a new initial public version with significant changes compared to the previous initial version [v0.9.0](#v090) and is not backward compatible.**

  - Within notifications the schema `EventNotification`has been replace by `CloudEvent` in accordance with the updated CAMARA Design Guidelines
  - If within `device` an IPv6 address is used it must be a single IPv6 address (out of the prefix used by the device)
- This release includes changes to be compliant with the [Design Guidelines](https://github.com/camaraproject/Commonalities/blob/release-0.2.0/documentation/API-design-guidelines.md#10-security) and other documents in [release v0.2 of CAMARA Commonalities](https://github.com/camaraproject/Commonalities/tree/release-0.2.0)
- This is another inital (v0.x) release and further releases before the first stable major v1.x release might introduce breaking changes (e.g. API changes to align with Commonalities updates)

**Main Changes**

* Aligned event notification with CloudEvent spec which will allow API consumers and implementators to use standard libraries and tools which are available to handle CloudEvents (https://cloudevents.io/)
* Added a new operation `/sessions/{sessionId}/extend` which allows to extend the duration of an active session 

- API definition **with inline documentation**:
  - [View it on ReDoc](https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/camaraproject/QualityOnDemand/r1.4/code/API_definitions/qod-api.yaml&nocors)
  - [View it on Swagger Editor](https://editor.swagger.io/?url=https://raw.githubusercontent.com/camaraproject/QualityOnDemand/r1.4/code/API_definitions/qod-api.yaml)
  - OpenAPI [YAML spec file](https://github.com/camaraproject/QualityOnDemand/blob/r1.4/code/API_definitions/qod-api.yaml)

### Added
 
* Added statusInfo 'DELETE_REQUESTED' for qosStatus 'UNAVAILABLE' and clarified notification events in documentation by @hdamker in https://github.com/camaraproject/QualityOnDemand/pull/258
* Added new endpoint to extend duration of an active session by @emil-cheung in https://github.com/camaraproject/QualityOnDemand/pull/216
* Added global tags element  by @rartych in https://github.com/camaraproject/QualityOnDemand/pull/227
* Added a new error example for DurationOutOfRangeForQoSProfile by @jlurien in https://github.com/camaraproject/QualityOnDemand/pull/259

### Changed

* Aligned event notification with CloudEvents spec by @jlurien in https://github.com/camaraproject/QualityOnDemand/pull/224
* Moved "description" out of "allOf" declaration by @maxl2287 in https://github.com/camaraproject/QualityOnDemand/pull/205
  * Note: this change shouldn't have an impact for API consumers but is relevant for implementations of the API.
* Single IP addresses in Device model specified with standard formats instead of patterns by @jlurien in https://github.com/camaraproject/QualityOnDemand/pull/237
* Moved "basePath" /qod/v0 to "url"-property and introduced "apiroot" in definition of server  @maxl2287 in https://github.com/camaraproject/QualityOnDemand/pull/252

### Fixed

* na
  
### Removed

* na

## New Contributors
* @ravindrapalaskar17 made their first contribution in https://github.com/camaraproject/QualityOnDemand/pull/215
* @rartych made their first contribution in https://github.com/camaraproject/QualityOnDemand/pull/227

**Full Changelog**: https://github.com/camaraproject/QualityOnDemand/compare/v0.9.0...r1.4

# r1.3 - rc

## Release Notes

This release contains the definition and documentation of
* quality-on-demand v0.10.0-rc.2

## quality-on-demand v0.10.0-rc.2

**quality-on-demand v0.10.0-rc.2 is the second release-candidate version for v0.10.0 of the Quality-On-Demand (QoD) API.**

- API definition **with inline documentation**:
  - [View it on ReDoc](https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/camaraproject/QualityOnDemand/r1.3/code/API_definitions/qod-api.yaml&nocors)
  - [View it on Swagger Editor](https://editor.swagger.io/?url=https://raw.githubusercontent.com/camaraproject/QualityOnDemand/r1.3/code/API_definitions/qod-api.yaml)
  - OpenAPI [YAML spec file](https://github.com/camaraproject/QualityOnDemand/blob/r1.3/code/API_definitions/qod-api.yaml)

### Added

* Added a new error example for DurationOutOfRangeForQoSProfile by @jlurien in https://github.com/camaraproject/QualityOnDemand/pull/259
* Added a note to maxDuration parameter within qosProfile schema about the limit of 86400 seconds by @hdamker in https://github.com/camaraproject/QualityOnDemand/pull/256
* Added statusInfo 'DELETE_REQUESTED' for qosStatus 'UNAVAILABLE' and clarified notification events in documentation by @hdamker in https://github.com/camaraproject/QualityOnDemand/pull/258:
  * notifications will be sent for all changes of QosStatus, even if initiated by the client.
  * what will happen when qosStatus changes from 'AVAILABLE' to 'UNAVAILABLE' due to 'NETWORK_TERMINATED'

### Changed

* Moved "basePath" /qod/v0 to "url"-property and introduced "apiroot" in definition of server  @maxl2287 in https://github.com/camaraproject/QualityOnDemand/pull/252

### Fixed

* na
  
### Removed

* na

**Full Changelog**: https://github.com/camaraproject/QualityOnDemand/compare/r1.2...r1.3

# r1.2 - rc

## Release Notes

This release contains the definition and documentation of
* quality-on-demand v0.10.0-rc.1

## quality-on-demand v0.10.0-rc.1

**quality-on-demand v0.10.0-rc.1 is the first release-candidate version for v0.10.0 of the Quality-On-Demand (QoD) API.** 

- **The version contains significant changes compared to v0.9.0, and it is not backward compatible:**
  - Within notifications the schema `EventNotification`has been replace by `CloudEvent` in accordance with the updated CAMARA Design Guidelines
  - If within `device` an IPv6 address is used it must be a single IPv6 address (out of the prefix used by the device)
- **This is only the pre-release, it should be considered as a draft of the upcoming release v0.10.0**
  - The pre-release is meant for implementors, but it is not recommended to use the API with customers in productive environments.

**Main Changes**

* Aligned event notification with CloudEvent spec which will allow API consumers and implementators to use standard libraries and tools which are available to handle CloudEvents (https://cloudevents.io/)
* Added a new operation `/sessions/{sessionId}/extend` which allows to extend the duration of an active session

- API definition **with inline documentation**:
  - [View it on ReDoc](https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/camaraproject/QualityOnDemand/r1.2/code/API_definitions/qod-api.yaml&nocors)
  - [View it on Swagger Editor](https://editor.swagger.io/?url=https://raw.githubusercontent.com/camaraproject/QualityOnDemand/r1.2/code/API_definitions/qod-api.yaml)
  - OpenAPI [YAML spec file](https://github.com/camaraproject/QualityOnDemand/blob/r1.2/code/API_definitions/qod-api.yaml)

### Added

* Added new endpoint to extend duration of an active session by @emil-cheung in https://github.com/camaraproject/QualityOnDemand/pull/216
* Added global tags element by @rartych in https://github.com/camaraproject/QualityOnDemand/pull/227

### Changed

* Align event notification with CloudEvents spec by @jlurien in https://github.com/camaraproject/QualityOnDemand/pull/224
* Moved "description" out of "allOf" declaration by @maxl2287 in https://github.com/camaraproject/QualityOnDemand/pull/205
  * Note: this change shouldn't have an impact for API consumers but is relevant for implementations of the API.
* Aligned with changes in https://github.com/camaraproject/Template_Lead_Repository on test definitions by @rartych in https://github.com/camaraproject/QualityOnDemand/pull/233
* Single IP addresses in Device model specified with standard formats instead of patterns by @jlurien in https://github.com/camaraproject/QualityOnDemand/pull/237

### Fixed

* NA
  
### Removed

* NA

## New Contributors
* @ravindrapalaskar17 made their first contribution in https://github.com/camaraproject/QualityOnDemand/pull/215
* @rartych made their first contribution in https://github.com/camaraproject/QualityOnDemand/pull/227

**Full Changelog**: https://github.com/camaraproject/QualityOnDemand/compare/v0.9.0...r1.2

# r1.1 - alpha

## Release Notes

This release contains the definition and documentation of
* quality-on-demand v0.10.0-alpha.1

## quality-on-demand v0.10.0-alpha.1

- **This version contains significant changes compared to v0.9.0, and it is not backward compatible**
  - Especially a lot of the parameter names changed in line with the agreed glossary within CAMARA Commonalities
- **This is only a pre-release, it should be considered as a draft of the upcoming release v0.10.0**
- The pre-release is meant for implementors, but it is not recommended to use the API with customers in productive environments.

- [API definition with inline documentation](https://github.com/camaraproject/QualityOnDemand/blob/r1.1/code/API_definitions/qod-api.yaml)

### Added

* Added new endpoint to extend duration of an active session by @emil-cheung in https://github.com/camaraproject/QualityOnDemand/pull/216
* Introduced of linting with Megalinter and Swagger Editor Validator by @RandyLevensalor, @maxl2287 and @ravindrapalaskar17 in https://github.com/camaraproject/QualityOnDemand/pull/206, https://github.com/camaraproject/QualityOnDemand/pull/207, https://github.com/camaraproject/QualityOnDemand/pull/212, and  https://github.com/camaraproject/QualityOnDemand/pull/215
* Added global tags element by @rartych in https://github.com/camaraproject/QualityOnDemand/pull/227

### Changed

* Aligned event notification with CloudEvents spec by @jlurien in https://github.com/camaraproject/QualityOnDemand/pull/224
* Moved "description" out of "allOf" declaration by @maxl2287 in https://github.com/camaraproject/QualityOnDemand/pull/205
  * Note: this change shouldn't have an impact for API consumers but is relevant for implementations of the API.

### Fixed

* NA
  
### Removed

* NA

## New Contributors
* @ravindrapalaskar17 made their first contribution in https://github.com/camaraproject/QualityOnDemand/pull/215
* @rartych made their first contribution in https://github.com/camaraproject/QualityOnDemand/pull/227

**Full Changelog**: https://github.com/camaraproject/QualityOnDemand/compare/v0.9.0...r1.1

# v0.9.0

NOTE: Original content for older releases has been removed from the example
