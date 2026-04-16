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

### 4.4. Proof Presentation (OID4VP)

For presenting the proof of age, the user's app will generate a **Zero-Knowledge Proof (ZKP)**. This allows the user to prove the validity of the `over_18` claim to a verifier without revealing any other personal information. This presentation will follow the **OpenID for Verifiable Presentations (OID4VP)** protocol.

## 5. Security Considerations

*   **Signature Verification:** Verifiers MUST validate the digital signature of the attestation. The public key of the Vonage Signing Engine (QTSP) must be available to verifiers through a trusted registry (e.g., the eIDAS Trusted List).
*   **Data Minimization:** The use of ZKPs ensures that only the necessary information (i.e., the truth of the age claim) is shared with the verifier.
*   **Secure Communication:** All communication between components must be secured using TLS.

## 6. Compliance

This specification is designed to be compliant with the European Digital Identity Wallet architecture.

*   **Protocols:** The use of **OIDC**, **OID4VCI**, and **OID4VP** aligns with the core standards.
*   **Attestation Format:** The **`mso_mdoc`** format is used, as required.
*   **Proof Type:** Proofs will be in **JWT** format.
*   **PKCE:** Proof Key for Code Exchange (PKCE) will be used for enhanced security in the OIDC authorization flow.

## 7. Codebase Mapping

*   **`Issuer Service (EU Blueprint)`:** This corresponds to the application in the **`av-srv-web-issuing-avw-py/`** directory. This service will be configured, but its core logic will not be significantly modified.
*   **`Signing Engine (QEAA Seal)`:** This is a logical component within the `Issuer Service`. It is not a separate service but refers to the part of the blueprint that must be configured with Vonage's production QTSP certificates and private keys.
*   **`Vonage Identity Provider (OIDC)`:** This is a **new service** that must be designed and built. It will contain the custom logic for interacting with the Aduna Hub and MNOs.