# Specification: Vonage as Age Attestation Issuer

This document provides a specification for a system where Vonage acts as the issuer of age attestations, integrating with mobile network operators (MNOs) for identity and age verification.

## 1. Scope

This specification covers the end-to-end process of a user obtaining a verifiable "Proof of Age" attestation from Vonage. The process begins with the user initiating a request from a mobile application and concludes with the issuance of a signed attestation to the user's digital wallet.

The primary use case is to allow users to prove they are over a certain age (e.g., 18) to a third-party verifier without revealing their actual date of birth.

## 2. High-Level Architecture

The overall architecture and sequence of events are described in the [architecture.md](architecture.md) document.

## 3. Actors and Components

The system comprises the following key actors and components:

*   **User:** The individual seeking to obtain a proof of age.
*   **EU Age Verification App:** A mobile application that the user interacts with to manage their digital identity and credentials.
*   **Vonage (Issuer):**
    *   **Issuer Service:** The core service responsible for orchestrating the age verification and attestation issuance process.
    *   **Signing Keys (QTSP):** A Qualified Trust Service Provider responsible for digitally signing the attestations to ensure their authenticity and integrity.
*   **Aduna Global Hub:** An aggregation hub that provides a unified interface to multiple Mobile Network Operators (MNOs) via the CAMARA API.
*   **Mobile Network Operator (MNO):** The telecommunications provider that holds the user's KYC (Know Your Customer) data, including their date of birth.
*   **Verifier:** Any entity that needs to verify a user's age (e.g., online services, retail stores, venues).

## 4. Technical Details

### 4.1. Credential Issuance Protocol

The issuance process will follow the **OpenID for Verifiable Credential Issuance (OID4VCI)** standard. The EU Age Verification App will initiate an OID4VCI flow to request the credential from the Vonage Issuer Service.

### 4.2. Age Verification

The user's age will be verified through the following steps:

1.  The Vonage Issuer Service will receive the user's phone number from the app.
2.  It will query the **Aduna Global Hub** using the **CAMARA `NumberVerification` API** to confirm possession of the phone number and the **CAMARA `AgeVerification` API** to check if the user is over the required age.
3.  Aduna will route the request to the appropriate MNO.
4.  The MNO will check its KYC records for the user's date of birth, calculate the age, and return a boolean response (e.g., `true` if over 18).

### 4.3. Attestation Format

The age attestation will be issued in the **`mso_mdoc` (Mobile Security Object for Mobile Documents)** format, as specified by ISO/IEC 18013-5. The attestation will contain a single claim, such as `over_18: true`.

### 4.4. Proof Presentation

For presenting the proof of age, the user's app will generate a **Zero-Knowledge Proof (ZKP)**. This allows the user to prove the validity of the `over_18` claim to a verifier without revealing any other personal information contained within the `mso_mdoc`.

## 5. Security Considerations

*   **Signature Verification:** Verifiers MUST validate the digital signature of the attestation. The public key of the Vonage Signing Keys (QTSP) must be available to verifiers through a trusted registry.
*   **Data Minimization:** The use of ZKPs ensures that only the necessary information (i.e., the truth of the age claim) is shared with the verifier. The user's date of birth or other personal data is not exposed during verification.
*   **Secure Communication:** All communication between components must be secured using TLS.
*   **Phone Number Verification:** The initial step of verifying phone number ownership via the CAMARA API is crucial to bind the user to the identity held by the MNO.

## 6. Compliance

This specification is designed to be compliant with the European Age Verification Solution's technical standards.

*   **Protocol:** The use of **OID4VCI** aligns with the specified "Authorization Code flow".
*   **Attestation Format:** The **`mso_mdoc`** format is used, as required.
*   **Proof Presentation:** The use of **Zero-Knowledge Proofs (ZKP)** is in line with the recommendations for privacy-preserving age verification.
*   **Namespace:** The attestation will use the namespace `eu.europa.ec.av.1`.
*   **Proof Type:** Proofs will be in **JWT** format.
*   **PKCE:** Proof Key for Code Exchange (PKCE) will be used for enhanced security in the authorization flow.
