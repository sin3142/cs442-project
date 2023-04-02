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
<!-- | Record ID | `rid` | `any`, `R001@SGH`, `R002@NHG` | -->
| Patient ID | `pid` | `any`, `P001@SGH`, `P002@NHG` |
| Qualification | `qual` | `doctor@MOH`, `nurse@MOH`, `pharmacist@MOH` |
| Specialty | `spt` | `surgery@MOH`, `cardiology@MOH`, `pediatrics@MOH`, `pathology@MOH` |
| Purpose | `prp` | `billing@SGH`, `research@SH`, `insurance@RMG` |
| Group ID | `gid` | `any`, `G001@SGH`, `G002@NHG` |
| Clearance | `clr` | `low`, `med`, `high` |

## Types of Medical Records

| Record Type | ID | Example Policy |
| --- | --- | --- |
| Patient profile | `profile` | `rid or pid or qual=doctor or clr=low or (prp and grp)*` |
| Allergies | `allergies` | `rid or pid or qual=doctor or qual@MOH=nurse and clr=low or (prp and grp)*` |
| Medical history | `history` | `rid or pid or qual=doctor or clr=med or (prp and grp)*` |
| Prescriptions | `prescriptions` | `rid or pid or qual=doctor and spt* or qual=pharmacist` |
| Vaccinations | `vaccinations` | `rid or pid or qual=doctor or qual=nurse` |
| Discharge summary | `discharge_summary` | `rid or qual=doctor and spt*` |
| Test results | `test` | `rid or clr=high` |
| Medical bill | `bill` | `rid or pid or prp=billing or (prp and grp)*` |

## Demo

### Parties

#### Data Owners

- Singapore General Hospital (SGH) - specialises in surgery
- Singapore Polyclinics (SP) - high accessibility
- KK Women's and Children's Hospital (KK) - specialises in pediatrics
- Mount Elizabeth Hospital (MEH) - specialises in cardiology

#### Attribute Authorities

- Ministry of Health (MOH) - issues qualifications and specialities
- SingHealth (SH) - issue attributes for SGH, SP and KK
- MEH - issues attributes for MEH

#### Users & Attributes

| User | Patient ID | Qualification | Specialty | Purpose | Group ID | Clearance |
| --- | --- | --- | --- | --- | --- | --- |
| Doctor Tan | - | `doctor@MOH` | `surgery@MOH`, `pathology@MOH` | - | - | `low@SH`, `med@SH`, `high@SH` |
| Doctor Lim | - | `doctor@MOH` | `pediatrics@MOH` | - | - | `low@SH`, `med@SH` |
| Doctor Lee | - | `doctor@MOH` | `cardiology@MOH` | - | - | `low@SH`, `med@SH`, `high@MEH` |
| Doctor Ng | - | `doctor@MOH` | - | - | - | `low@SH`, `med@SH` |
| Nurse Tay | - | `nurse@MOH` | - | - | - | `low@SGH` |
| Pharmacist Wong | - | `pharmacist@MOH` | - | - | - | - |
| Researcher Goh | - | - | - | `research@SH` | `R001@SH` | |
| Insurance Agent Chua | - | - | - | `insurance@MEH`, `insurance@SH` | `I001@MEH`, `I001@SH` | |
| Patient Chan | `P001@SH` | - | - | - | - | - |
| Patient Koh | `P002@SH` | - | - | - | - | - |
| Patient Teo | `P003@SH` | - | - | - | - | - |
| Patient Ang | `P004@MEH` | - | - | - | - | - |

### Scenarios

#### Scenario 1: Emergency Treatment

- Patient Chan goes to Singapore Polyclinics (SP) for his regular checkups.
- Patient Chan suffers a heart attack and is admitted to Mount Elizabeth Hospital (MEH)
- Doctor Lee is a cardiologist at MEH.
- Doctor Lee needs to access Patient Chan's medical history and discharge summary to determine the best course of treatment.
- Patient Chan's medical history is encrypted with the following policy:
    `'rid@SH=R001' or 'pid@SH=P001' or 'qual@MOH=doctor' or 'clr@SH=med'"`.
- Patient Chan's discharge summary is encrypted with the following policy:
    `'rid@SH=R002' or 'qual@MOH=doctor' and 'spt@MOH=cardiology'`
- Doctor Lee authenticates his ownership of the attributes `qual@MOH=doctor` and `spt@MOH=cardiology` to MOH and receives decryption keys for the attributes.
- Doctor Lee is able to decrypt the medical history and discharge summary, and uses them to determine the best course of treatment for Patient Chan.

#### Scenario 2: Inpatient Treatment

- Patient Chan is hospitalised at MEH for a week.
- Nurse Tay is a nurse at SGH.
- Nurse Tay needs to access Patient Chan's allergies and vaccinations to administer the correct medication.
- Patient Chan's allergies are encrypted with the following policy:
    `'rid@SH=R003' or 'pid@SH=P001' or 'qual@MOH=doctor' or 'qual@MOH=nurse' and 'clr@SH=low'`.
- Patient Chan's vaccinations are encrypted with the following policy:
    `'rid@SH=R004' or 'pid@SH=P001' or 'qual@MOH=doctor' or 'qual@MOH=nurse'`.
- Nurse Tay authenticates her ownership of the attributes `qual@MOH=nurse` to MOH and receives decryption key for the attribute.
- Nurse Tay authenticates her ownership of the attributes `clr@SH=low` to SH and receives decryption key for the attribute.
- Nurse Tay is able to decrypt the allergies and vaccinations, and uses them to administer the correct medication to Patient Chan.

#### Scenario 3: Insurance

- After being discharged from MEH, Patient Chan is charged a medical bill of $1000.
- Patient Chan's insurance agent, Agent Chua, needs to access Patient Chan's medical bill to submit it to the insurance company for reimbursement.
- Patient Chan's medical bill is encrypted with the following policy:
    `'rid@MEH=R001' or 'pid@MEH=P001' or 'prp@MEH=billing' or ('prp@SH=insurance' and 'grp@SH=I001')`.
- Agent Chua authenticates his ownership of the attributes `prp=insurance@MEH` and `grp=AIA@MEH` to MEH and receives decryption keys for the attributes.
- Agent Chua is able to decrypt the medical bill and submits it to the insurance company for reimbursement.

#### Scenario 4: Prescription

- Patient Chan is prescribed a new medication by Doctor Lee, and needs to collect it from Unity Pharmacy.
- Pharmacist Wong is a pharmacist at Unity Pharmacy.
- Pharmacist Wong needs to verify the prescription to ensure that the medication is safe for Patient Chan.
- Patient Chan's prescription is encrypted with the following policy:
    `'rid@MEH=R002' or 'pid@MEH=P001' or 'qual@MOH=doctor' or 'qual@MOH=pharmacist'`.
- Pharmacist Wong authenticates his ownership of the attributes `qual@MOH=pharmacist` to MOH and receives decryption key for the attribute.
- Pharmacist Wong is able to decrypt the prescription and verifies that the medication is safe for Patient Chan.

#### Scenario 5: Patient Data

- Patient Teo just went through a routine checkup at KK Hospital (KK).
- Patient Teo wants to view his updated medical profile on his mobile phone.
- Patient Teo's medical profile is encrypted with the following policy:
    `'rid@KK=R001 or pid@KK=P001' or 'qual@MOH=doctor' or 'qual@MOH=nurse'`.
- Patient Teo authenticates his ownership of the attributes `pid@KK=P001` to KK and receives decryption key for the attribute.
- Patient Teo is able to decrypt the medical profile and views it on his mobile phone.

#### Scenario 6: Research

- Patient Koh is a patient at Singapore General Hospital (SGH).
- Patient Koh is participating in a research study on the effects of a new drug on patients with diabetes.
- The research team, Researcher Goh, needs to access Patient Koh's medical history and test results to determine the effects of the drug.
- The medical history is encrypted with the following policy: `rid@SGH=R001 or pid@SGH=P002 or qual=doctor@MOH or clr=med@SGH or (prp=research@SH and grp=SMU@SH)`.
- The test results are encrypted with the following policy: `rid@SGH=R001 or clr=high@SGH or (prp=research@SH and grp=SMU@SH)`.
- Researcher Goh authenticates his ownership of the attributes `prp=research@SH` and `grp=SMU@SH` to SH and receives decryption keys for the attributes.
- Researcher Goh is able to decrypt the medical history and test results, and uses them to determine the effects of the drug on Patient Koh.
