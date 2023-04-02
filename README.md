# CS442 Group Project: Cloud-based EMR System w/ dABE

## References

- KP-ABE: <https://eprint.iacr.org/2006/309.pdf>
- BSW07 CP-ABE: <https://www.cs.utexas.edu/~bwaters/publications/papers/cp-abe.pdf>
- W11 CP-ABE: <https://eprint.iacr.org/2008/290.pdf>
- LW11 dCP-ABE: <https://eprint.iacr.org/2010/351.pdf>
- RW15 dCP-ABE: <https://eprint.iacr.org/2015/016.pdf>

- MOH Useful Links: <https://www.moh.gov.sg/hpp/all-healthcare-professionals/useful-links>
- Healthcare Professionals Database: <https://www.moh.gov.sg/hpp/all-healthcare-professionals/healthcare-professionals-search>
- CDC Data: <https://www.cdc.gov/DataStatistics/>

## Attributes

| Attribute | ID | Example Values |
| --- | --- | --- |
| Record ID | `rid` | `any`, `R001@SGH`, `R002@NHG` |
| Patient ID | `pid` | `any`, `P001@SGH`, `P002@NHG` |
| Qualification | `qual` | `doctor@MOH`, `nurse@MOH`, `pharmacist@MOH` |
| Specialty | `spt` | `surgery@MOH`, `cardiology@MOH`, `pediatrics@MOH`, `pathology@MOH` |
| Purpose | `prp` | `billing@SGH`, `research@SH`, `insurance@RMG` |
| Group ID | `gid` | `any`, `G001@SGH`, `G002@NHG` |
| Clearance | `clr` | `low`, `med`, `high` |

## Types of Medical Records

| Record Type | ID | Example Policy |
| --- | --- | --- |
| Medical Profile | `profile` | `rid or pid or qual=doctor or clr=low or (prp and grp)*` |
| Allergies | `allergies` | `rid or pid or qual=doctor or qual@MOH=nurse and clr=low or (prp and grp)*` |
| Medical History | `history` | `rid or pid or qual=doctor or clr=med or (prp and grp)*` |
| Prescriptions | `prescriptions` | `rid or pid or qual=doctor and spt* or qual=pharmacist` |
| Discharge Summary | `discharge` | `rid or qual=doctor and spt*` |
| Test Results | `test` | `rid or clr=high` |
| Medical Bill | `bill` | `rid or pid or prp=billing or (prp and grp)*` |

## Demo

### Parties

#### Data Owners

- Singapore General Hospital (SGH) - specialises in surgery
- Singapore Polyclinics (SP) - high accessibility
- KK Women's and Children's Hospital (KK) - specialises in pediatrics
- Mount Elizabeth Hospital (MEH) - specialises in cardiology

#### Attribute Authorities

- Ministry of Health (MOH) - issues qualifications and specialities
- SingHealth (SH) - issue attributes for SP, SGH and KK
- MEH - issues attributes for MEH

#### Users & Attributes

| User | Patient ID | Qualification | Specialty | Purpose | Group ID | Clearance |
| --- | --- | --- | --- | --- | --- | --- |
| Doctor Tan | - | `qual@MOH=doctor` | `spt@MOH=surgery` | - | - | `clr@SH=low`, `clr@SH=med`, `clr@MEH=high` |
| Doctor Lee | - | `qual@MOH=doctor` | `spt@MOH=cardiology` | - | - | `clr@MEH=low`, `clr@MEH=med`, `clr@MEH=high` |
| Doctor Lim | - | `qual@MOH=doctor` | `spt@MOH=pediatrics` | - | - | `clr@SH=low`, `clr@SH=med`, `clr@SH=high` |
| Nurse Tay | - | `qual@MOH=nurse` | - | - | - | `clr@MEH=low`, `clr@MEH=med` |
| Pharmacist Wong | - | `qual@MOH=pharmacist` | - | - | - | - |
| Researcher Goh | - | - | - | `prp@SH=research` | `grp@SH=SMU` | |
| Insurance Agent Chua | - | - | - | `prp@MEH=insurance`, `prp@SH=insurance` | `grp@MEH=AIA`, `grp@SH=AIA` | |
| Patient Chan | `pid@SH=001`, `pid@MEH=001` | - | - | - | - | - |
| Patient Teo | `pid@SH=002` | - | - | - | - | - |
| Patient Koh | `pid@SH=003` | - | - | - | - | - |

### Scenarios

#### Scenario 1: Emergency Treatment

- Patient Chan goes to Singapore Polyclinics (SP) for his regular checkups.
- Patient Chan suffers a heart attack and is admitted to Mount Elizabeth Hospital (MEH)
- Doctor Lee is a cardiologist at MEH.
- Doctor Lee needs to access Patient Chan's medical history and discharge summary to determine the best course of treatment.
- Patient Chan's medical history is encrypted with the following policy:
    `'rid@SH=001' or 'pid@SH=001' or 'qual@MOH=doctor' or 'clr@SH=med'`.
- Patient Chan's discharge summary is encrypted with the following policy:
    `'rid@SH=002' or 'qual@MOH=doctor' and 'spt@MOH=cardiology'`
- Doctor Lee authenticates his ownership of the attributes `qual@MOH=doctor` and `spt@MOH=cardiology` to MOH and receives decryption keys for the attributes.
- Doctor Lee is able to decrypt the medical history and discharge summary, and uses them to determine the best course of treatment for Patient Chan.

#### Scenario 2: Inpatient Treatment

- Patient Chan is hospitalised at MEH for a week.
- Nurse Tay is a nurse at MEH.
- Nurse Tay needs to access Patient Chan's drug allergies to administer the correct medication.
- Patient Chan's drug allergies are encrypted with the following policy:
    `'rid@MEH=001' or 'pid@MEH=001' or 'qual@MOH=doctor' or 'qual@MOH=nurse' and 'clr@MEH=low'`.
- Nurse Tay authenticates her ownership of the attributes `qual@MOH=nurse` to MOH and receives decryption key for the attribute.
- Nurse Tay authenticates her ownership of the attributes `clr@MEH=low` to MEH and receives decryption key for the attribute.
- Nurse Tay is able to decrypt the drug allergies, and uses them to administer the correct medication to Patient Chan.

#### Scenario 3: Insurance

- After being discharged from MEH, Patient Chan is charged a medical bill.
- Patient Chan's insurance agent, Agent Chua, needs to access Patient Chan's medical bill to submit it to the insurance company for reimbursement.
- Patient Chan's medical bill is encrypted with the following policy:
    `'rid@MEH=002' or 'pid@MEH=001' or 'prp@MEH=billing' or ('prp@MEH=insurance' and 'grp@MEH=AIA')`.
- Agent Chua authenticates his ownership of the attributes `prp@MEH=insurance` and `grp@MEH=AIA` to MEH and receives decryption keys for the attributes.
- Agent Chua is able to decrypt the medical bill and submits it to the insurance company for reimbursement.

#### Scenario 4: Prescription

- Patient Chan is prescribed a new medication by Doctor Lee, and needs to collect it from Unity Pharmacy.
- Pharmacist Wong is a pharmacist at Unity Pharmacy.
- Pharmacist Wong needs to verify the prescription to ensure that the medication is safe for Patient Chan.
- Patient Chan's prescription is encrypted with the following policy:
    `'rid@MEH=003' or 'pid@MEH=001' or 'qual@MOH=doctor' or 'qual@MOH=pharmacist'`.
- Pharmacist Wong authenticates his ownership of the attributes `qual@MOH=pharmacist` to MOH and receives decryption key for the attribute.
- Pharmacist Wong is able to decrypt the prescription and verifies that the medication is safe for Patient Chan.

#### Scenario 5: Patient Data

- Patient Teo just went through a routine checkup at KK Hospital (KK).
- Patient Teo wants to view his updated medical profile on his mobile phone.
- Patient Teo's medical profile is encrypted with the following policy:
    `'rid@SH=001' or 'pid@SH=002' or 'qual@MOH=doctor' or 'qual@MOH=nurse'`.
- Patient Teo authenticates his ownership of the attributes `pid@SH=002` to SH and receives decryption key for the attribute.
- Patient Teo is able to decrypt the medical profile and views it on his mobile phone.

#### Scenario 6: Research

- Patient Koh is a patient at Singapore General Hospital (SGH).
- Patient Koh is participating in a research study on the effects of a new drug on patients with diabetes.
- The research team, Researcher Goh, needs to access Patient Koh's medical history and test results to determine the effects of the drug.
- The medical history is encrypted with the following policy: `'rid@SH=001' or 'pid@SH=003' or 'qual@MOH=doctor' or 'clr@SH=med' or ('prp@SH=research' and 'grp@SH=SMU')`.
- The test results are encrypted with the following policy: `'rid@SH=R001' or 'clr@SH=high' or ('prp@SH=research' and 'grp@SH=SMU')`.
- Researcher Goh authenticates his ownership of the attributes `prp@SH=research` and `grp@SH=SMU` to SH and receives decryption keys for the attributes.
- Researcher Goh is able to decrypt the medical history and test results, and uses them to determine the effects of the drug on Patient Koh.

### List of Documents

| Record Type | Record ID | Hospital | Patient ID | Patient Name | Access Policy |
| --- | --- | --- | --- | --- | --- |
| Medical History | 001 | SP | 001 | Patient Chan | `'rid@SH=001' or 'pid@SH=001' or 'qual@MOH=doctor' or 'clr@SH=med'` |
| Discharge Summary | 002 | SP | 001 | Patient Chan | `'rid@SH=002' or 'qual@MOH=doctor' and 'spt@MOH=cardiology'` |
| Drug Allergies | 001 | MEH | 001 | Patient Chan | `'rid@MEH=001' or 'pid@MEH=001' or 'qual@MOH=doctor' or 'qual@MOH=nurse' and 'clr@MEH=low'` |
| Medical Bill | 002 | MEH | 001 | Patient Chan | `'rid@MEH=002' or 'pid@MEH=001' or 'prp@MEH=billing' or 'prp@MEH=insurance' and 'grp@MEH=AIA'` |
| Prescription | 003 | MEH | 001 | Patient Chan | `'rid@MEH=003' or 'pid@MEH=001' or 'qual@MOH=doctor' or 'qual@MOH=pharmacist'` |
| Medical Profile | 001 | KK | 002 | Patient Teo | `'rid@SH=001' or 'pid@SH=002' or 'qual@MOH=doctor' or 'qual@MOH=nurse'` |
| Medical History | 001 | SGH | 003 | Patient Koh | `'rid@SH=001' or 'pid@SH=003' or 'qual@MOH=doctor' or 'clr@SH=med' or 'prp@SH=research' and 'grp@SH=SMU'` |
| Test Results | 002 | SGH | 003 | Patient Koh | `'rid@SH=R001' or 'clr@SH=high' or ('prp@SH=research' and 'grp@SH=SMU')` |
