# Implementation Plan: Vonage Age Verification Service

This plan outlines the development phases for creating the Vonage Age Verification solution, based on the architecture defined in `architecture.md`.

## Phase 1: Environment Setup & Blueprint Familiarization

The goal of this phase is to get the standard EU Blueprint software running "as-is" to understand its mechanics before we modify its configuration.

*   **Task 1.1: Set Up Development Environment**
    *   Follow the `install.md` guide in the `av-srv-web-issuing-avw-py` directory.
    *   Install all prerequisites: Python 3.9/3.10, Flask, and any other dependencies listed.
    *   **Goal:** Have a clean, working environment for the blueprint software.

*   **Task 1.2: Run the Blueprint with Default Settings**
    *   Launch the EU Issuer Service locally.
    *   Use the built-in "simple form" authentication method to issue a test credential.
    *   **Goal:** Confirm the blueprint software works out-of-the-box and understand the default user flow for issuance.

*   **Task 1.3: Explore Configuration**
    *   Review the configuration files and documentation (`api_docs/configuration.md`).
    *   Identify where the authentication provider, signing keys, and issuer metadata are defined.
    *   **Goal:** Understand exactly which files need to be changed to integrate our custom components.

---

## Phase 2: Build the `Vonage Identity Provider (OIDC)`

This is the core development phase where we build our new, custom service.

*   **Task 2.1: Create the Service Scaffold**
    *   Create a new directory for the `Vonage Identity Provider` service.
    *   Initialize a new Python project (e.g., using Flask or FastAPI).
    *   Select and install a robust OIDC/OAuth library (e.g., `Authlib`) to handle the protocol complexities.
    *   **Goal:** A new, runnable service that can be developed independently.

*   **Task 2.2: Implement Mock OIDC Endpoints**
    *   Implement the essential OIDC endpoints (`/authorize`, `/token`, `/jwks.json`, `/.well-known/openid-configuration`).
    *   At this stage, the service should not perform any real verification. It should simulate a successful login and complete the OIDC authorization code flow, issuing an authorization code that the Wallet exchanges for an `access_token` and `id_token` at `/token`.
    *   **Goal:** A "dummy" OIDC provider that follows the correct protocol flow (auth code → token exchange → credential request).

*   **Task 2.3: Integrate with Aduna/CAMARA API**
    *   Develop a module within the OIDC provider to handle communication with the Aduna Global Hub.
    *   Implement the API client logic to call the CAMARA `Verify Age` endpoint.
    *   Connect this module to the `/authorize` endpoint. The OIDC flow should now only succeed if the Aduna API returns a `true` result.
    *   **Goal:** The OIDC provider can now perform real age verification via the MNO.

### Vonage Code Added to the Blueprint

Rather than building a fully separate OIDC provider service, the Vonage authentication logic was integrated directly into the EU Blueprint issuer. The following files were added or modified:

| File | Change |
|------|--------|
| `av-srv-web-issuing-avw-py/app/authn/vonage_oidc_auth.py` | **New file.** Custom `VonageOidcAuth` class extending `PidIssuerAuth`. Intercepts the authorization flow and redirects the user to the `/phone_form` endpoint instead of the default EU login page. |
| `av-srv-web-issuing-avw-py/app/camara_client.py` | **New file.** `CamaraClient` class that wraps the Vonage/Aduna CAMARA `Verify Age` API. Currently contains a stub returning `True`; to be replaced with the real API call. |
| `av-srv-web-issuing-avw-py/app/route_oidc.py` | **Modified.** Added `/phone_form` (GET) and `/verify_phone` (POST) routes. `/verify_phone` calls `CamaraClient.verify_age()`, then completes the OIDC authorization session and issues the authorization code. Also fixed `authorizationv2()` to redirect the browser directly to `/authorization` (rather than making an internal server-side HTTP call), and patched `redirect_uris` into the client CDB entry after `process_request_authorization()`. Added a null-guard in the `/token` endpoint for missing session IDs. |
| `register_client.py` | **New file** (project root). A one-shot script to register `my-awesome-client` with `redirect_uri=https://client.example.com/cb` against the local issuer's `/registration` endpoint. |

---

## Phase 3: Integration and Configuration

This phase connects the two main components together.

*   **Task 3.1: Configure Issuer to Trust the OIDC Provider** ✅ *Completed*
    *   Rather than a separate OIDC provider, the Vonage authentication logic was integrated directly into the EU Blueprint issuer (see `VonageOidcAuth` in Phase 2 table above).
    *   The `VonageOidcAuth` class is registered as the auth handler in the blueprint config, intercepting all authorization requests and routing them through `/phone_form` → CAMARA age check → auth code issuance.
    *   **Goal achieved:** The blueprint redirects all authentication requests through the Vonage/CAMARA verification flow.

*   **Task 3.2: Configure Production Signing Keys**
    *   Update the `Issuer Service` configuration to use Vonage's actual QTSP signing keys and certificates instead of the provided test ones. This will likely involve secure key management practices.
    *   **Goal:** Issued credentials are now signed with Vonage's official, verifiable signature.

---

## Phase 4: End-to-End Testing & Deployment

*   **Task 4.1: Full Flow Testing** ✅ *Completed (happy path)*
    *   The end-to-end issuance flow has been validated locally: OID4VCI credential request → OIDC redirect → phone form → CAMARA age check → auth code → token exchange (`access_token`, `id_token`, `refresh_token`) → `/credential` endpoint.
    *   The CAMARA client (`camara_client.py`) currently uses a stub returning `True`. Testing of failure cases (underage, MNO lookup failure, consent denied) is pending the real CAMARA API integration.
    *   **Remaining:** Negative-path testing once the real CAMARA API is wired up.

*   **Task 4.2: Containerize and Deploy**
    *   The Vonage authentication logic is integrated into the EU Blueprint issuer, so only a single service needs to be containerized. A `Dockerfile` already exists in `av-srv-web-issuing-avw-py/`.
    *   Update the `Dockerfile` and any environment configuration to include the new Vonage-specific env vars (`SERVICE_URL`, CAMARA credentials, etc.).
    *   Deploy to a staging environment and re-run the end-to-end flow against the real CAMARA API.
    *   **Goal:** A deployable, production-ready application with real age verification.
