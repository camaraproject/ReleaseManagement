# API Readiness Checklist

## Purpose

The API readiness checklist identifies the set of release assets to be provide before releasing an API. 
The applicable list is dependent on the targetted API status (alpha, release-candidate, public (initial or stable)).

The following table provides the explanation and location of each asset in the API repository.

| Nr | Release assets                          | Description       | Location |
|----|-----------------------------------------|-------------------|----------|
|  1  | Release Plan                            |   The release-plan.yaml file must be updated to reflect the targeted release   |  `{repository_home}/release-plan.yaml`  | 
|  2  | API Definition(s)                       |  There must be one API definition file {api-name}.yaml per API in the repository. The API must follow the applicable CAMARA Commonalities and ICM Guidelines.   | `/code/API_definitions/{api-name}.yaml` |
|  3  | API Documentation                       |   The API documentation must be provided inside the API definition file. Additional documentation may be provided as well.  | in API definition (yaml) (or in `/documentation/API_documentation/xxx.md`)|
|  4  | User Stories                            |  There must be at least one user story file in the repository. One user story may cover a single or multiple APIs. Each API needs to be covered by at least one user story. | `/documentation/API_documentation/{api-name}-xxx_User_Story.md` |
|  5  | Test Cases (basic)                      |   Basic API test cases must be provided covering sunny day scenarios  and main error cases, along with documentation. There must be at least one feature file per API, or alternatively, one for each operationId of an API.   | `/code/Test_definitions` |
|  6  | Test Cases (enhanced)                   |  Enhanced API test cases must be provided covering rainy day scenarios, along with documentation.   | `/code/Test_definitions` |
|  7  | API description link (for marketing)    |  A link to the API description on the CAMARA Wiki must be provided for each API for marketing purposes.   | `https://lf-camaraproject.atlassian.net/wiki/xxx` |

## Release assets per API status

The following table specifies which release assets are required for a given targeted API status

| Nr | Release assets                          | alpha | release-candidate |  initial<br>public | stable<br> public |
|----|-----------------------------------------|:-----:|:-----------------:|:------------------:|:------:|
| 1  | Release Plan                            |   M   |         M         |         M          |    M   | 
| 2  | API Definition(s)                       |   M   |         M         |         M          |    M   | 
| 3  | API Documentation                       |   M   |         M         |         M          |    M   | 
| 4  | User Stories                            |   O   |         O         |         O          |    M   | 
| 5  | Test Cases (basic)                      |   O   |         M         |         M          |    M   | 
| 5  | Test Cases (enhanced)                   |   O   |         O         |         O          |    M   | 
| 6  | Test result statement                   |   O   |         O         |         O          |    M   | 
| 7  | API description link(for marketing)     |   O   |         O         |         M          |    M   |

### API readiness checklist review

Before releasing the API (i.e. before issueing the /create-snapshot command in the Release Issue), the availability of all required assets for the targeted API status should be checked by the team.
If not yet available, the required release asset(s) should be added through PR(s) to `main` first.

Note: the current automated release process does not check the presence of all of the above items so a manual check by the team is needed. 
Further automated checks may be added later.

## See also

- [../README.md](../README.md) for documentation index
- [../deprecated/API-Readiness-Checklist.md](../deprecated/API-Readiness-Checklist.md) for the legacy template
