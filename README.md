# Specification: Vonage as Age Attestation Issuer

This document provides a specification for a system where Vonage acts as the issuer of age attestations. It follows a compliant architecture by separating the concerns of identity verification and credential issuance.

**Architectural Approach:**
1.  **Identity & Age Verification:** A new **`Vonage Identity Provider (OIDC)`** service will be built to verify a user's age via their Mobile Network Operator (MNO).
2.  **Credential Issuance:** The standard **`Issuer Service (EU Blueprint)`** software will be used, configured to trust the new OIDC service for authentication.

## 1. Scope

This specification covers the end-to-end process of a user obtaining a verifiable "Proof of Age" attestation from Vonage. The process begins with the user initiating a request from a mobile application and concludes with the issuance of a signed attestation to the user's digital wallet.

The primary use case is to allow users to prove they are over a certain age (e.g., 18) to a third-party verifier without revealing their actual date of birth.

## 2. High-Level Architecture

The overall architecture and sequence of events are described in the [architecture.md](architecture.md) document. This architecture is compliant with the EU framework by using OIDC for authentication before issuance.

## 3. Actors and Components

The system comprises the following key actors and components:

*   **User:** The individual seeking to obtain a proof of age.
*   **EUDI Wallet App:** A mobile application on the user's device that manages identity credentials.
*   **Vonage Services:**
    *   **Vonage Identity Provider (OIDC):** A new service that acts as an OpenID Connect provider. Its purpose is to authenticate a user by verifying their age via the Aduna Hub and MNO, then issuing a standard OIDC `ID Token`.
    *   **Issuer Service (EU Blueprint):** The standard Age Verification Issuer software. It is configured to trust the `Vonage Identity Provider`. It receives the `ID Token` as proof of authentication and then proceeds to issue the age attestation.
    *   **Signing Engine (QEAA Seal):** A logical component within the Issuer Service. It represents the Qualified Trust Service Provider (QTSP) functionality that signs the age attestation (`mso_mdoc`) with a Qualified Electronic Attestation of Attributes (QEAA) seal.
*   **Verification Hub (Aduna):** An intermediary service that connects to various Mobile Network Operators (MNOs) via the CAMARA API standard.
*   **Mobile Network Operator (MNO):** The user's mobile carrier, which holds Know Your Customer (KYC) data, including their date of birth.
*   **Verifier:** An entity that needs to verify a user's age (e.g., a cinema).

## 4. Technical Details

### 4.1. Authentication & Verification (OIDC)

The core of this architecture is the separation of authentication from issuance.

1.  When the `Issuer Service` receives a credential request, it will redirect the user's Wallet to the **`Vonage Identity Provider`** for authentication, following the standard OpenID Connect (OIDC) protocol.
2.  The `Vonage Identity Provider` will handle the age verification by querying the **Aduna Global Hub** using the CAMARA API.
3.  Upon successful verification, the `Vonage Identity Provider` will issue a standard OIDC **`ID Token`** back to the Wallet.

### 4.2. Credential Issuance (OID4VCI)

1.  The Wallet will present the `ID Token` to the `Issuer Service` as proof of a successful authentication event.
2.  The `Issuer Service`, trusting the `ID Token`, will proceed with creating the age attestation.
3.  The issuance process itself will follow the **OpenID for Verifiable Credential Issuance (OID4VCI)** standard.

### 4.3. Attestation Format

The age attestation will be issued in the **`mso_mdoc` (Mobile Security Object for Mobile Documents)** format, as specified by ISO/IEC 18013-5. The attestation will contain a single claim, such as `over_18: true`.

### 4.4. Proof Presentation (OID4VP / DC API)

When a user wants to access an age-restricted service, they present their `mso_mdoc` attestation to a verifier. The official AV ecosystem supports two presentation mechanisms:

1.  **Digital Credentials API (DC API)** — the preferred mechanism. A browser-integrated API (being standardised by W3C) that enables direct, privacy-preserving credential exchange between the verifier web page and the user's wallet on the same or nearby device. See: [w3.org/TR/digital-credentials](https://www.w3.org/TR/digital-credentials).
2.  **OpenID for Verifiable Presentations (OID4VP)** — the fallback mechanism for browsers that do not yet support the DC API. The user scans a QR code with the Age Verification App, approves the request with PIN/biometric, and the attestation is transmitted to the verifier.

In both cases, the `mso_mdoc` **selective disclosure** mechanism is used: the holder reveals only the required data elements (e.g. `over_18: true`) without exposing other fields such as date of birth. The verifier validates the issuer signature and checks the issuer against the **AV Trusted List**.

> **ZKP note:** Zero-Knowledge Proofs are documented as a future roadmap item in [Annex B of the AV Technical Specification](https://ageverification.dev/av-doc-technical-specification/docs/annexes/annex-B/annex-B-zkp/). They are not part of the current implementation. True ZKPs (e.g. BBS+ signatures) would require a different credential format and cryptographic stack to the current `mso_mdoc` selective disclosure approach.

## 5. Security Considerations

*   **Signature Verification:** Verifiers MUST validate the digital signature of the attestation. The public key of the Vonage Signing Engine (QTSP) must be available to verifiers through a trusted registry (e.g., the eIDAS Trusted List).
*   **Data Minimization:** The `mso_mdoc` selective disclosure mechanism ensures that only the required claim (e.g. `over_18: true`) is shared with the verifier, without revealing the underlying date of birth or any other personal data.
*   **Secure Communication:** All communication between components must be secured using TLS.

## 6. Quickstart

This section walks through the complete local end-to-end flow: from registering a client to receiving a signed access token and ID token.

### Prerequisites

*   Python 3.9/3.10 with the project virtualenv set up (see `av-srv-web-issuing-avw-py/install.md`).

### Step 1 — Start the issuer service

From the `av-srv-web-issuing-avw-py` directory:

```bash
source .venv/bin/activate
SERVICE_URL="http://127.0.0.1:5000/" flask --app app run
```

The `SERVICE_URL` environment variable must be set to the local address so that internal redirects resolve correctly.

### Step 2 — Register a client

From the project root (in a separate terminal):

```bash
python3 register_client.py
```

This registers `my-awesome-client` with `redirect_uri=https://client.example.com/cb`. A successful response returns a `client_id`, `client_secret`, and registration metadata (HTTP 201).

### Step 3 — Start the authorization flow

Open the following URL in a browser:

```
http://127.0.0.1:5000/authorizationV3?response_type=code&client_id=my-awesome-client&redirect_uri=https://client.example.com/cb&scope=openid
```

The server registers the client dynamically, then redirects the browser through `/authorization` → `/phone_form`.

### Step 4 — Enter a phone number

The phone form page asks for a phone number. Enter any value and click **Verify**. The `CamaraClient` calls the CAMARA `Verify Age` stub (always returns `true` in local/dev mode). On success the server completes the OIDC session and issues an authorization code.

### Step 5 — Capture the authorization code

The browser is redirected to:

```
https://client.example.com/cb?scope=openid&code=<AUTH_CODE>&iss=https%3A%2F%2F127.0.0.1%3A5000&client_id=my-awesome-client
```

Copy the value of the `code` parameter from the address bar.

### Step 6 — Exchange the code for tokens

```bash
curl -s -X POST http://127.0.0.1:5000/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data-urlencode "grant_type=authorization_code" \
  --data-urlencode "code=<AUTH_CODE>" \
  --data-urlencode "redirect_uri=https://client.example.com/cb" \
  --data-urlencode "client_id=my-awesome-client"
```

A successful response (HTTP 200) returns:

```json
{
  "token_type": "Bearer",
  "scope": "openid",
  "access_token": "<JWT>",
  "expires_in": 3600,
  "refresh_token": "<OPAQUE_TOKEN>",
  "id_token": "<JWT>"
}
```

*   The `access_token` is a signed ES256 JWT issued by the local server.
*   The `id_token` is a signed RS256 JWT containing the `sub`, `iss`, `aud`, `iat`, `exp`, and `acr` claims.
*   Both tokens have a 1-hour lifetime.




