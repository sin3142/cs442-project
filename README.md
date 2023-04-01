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
| Record ID | `rpt` | `any`, `R001@SGH`, `R002@NHG` |
| Patient ID | `pid` | `any`, `P001@SGH`, `P002@NHG` |
| Group ID | `gid` | `any`, `G001@SGH`, `G002@NHG` |
| Qualification | `qual` | `doctor@MOH`, `nurse@MOH`, `pharmacist@MOH` |
| Specialty | `spt` | `surgery@MOH`, `cardiology@MOH`, `pediatrics@MOH`  |
| Purpose | `prp` | `billing@SGH`, `research@SH`, `insurance@RMG` |
| Clearance | `clr` | `low`, `med`, `high` |

## Types of Medical Records

| Record Type | ID | Example Policy |
| --- | --- | --- |
| Medical conditions | `conditions` | `rid@SGH=R001 or pid@SGH=P001 or qual@MOH=doctor or (prp@SGH=research and grp@SGH=GR001) or (prp@SGH=insurance and grp@SGH=GI001)` |
| Discharge summary | `discharge_summary` | `rid@SGH=R002 or qual@MOH=doctor and spt@MOH=surgery` |
| Allergies | `allergies` | `rid@SGH=R003 or @pid@SGH=P001 or qual@MOH=doctor or qual@MOH=nurse or (prp@SGH=research and grp@SGH=GR002)` |
| Prescriptions | `prescriptions` | `rid@SGH=R004 or pid@SGH=P001 or qual@MOH=doctor or qual@MOH=pharmacist` |
| Vaccinations | `vaccinations` | `rid@SGH=R005 or pid@SGH=P001 or qual@MOH=doctor or qual@MOH=nurse` |
| Test results | `test_results` | `rid@SGH=R006 or clr@SGH=high` |
| Billing | `billing` | `rid@SGH=R007 or pid@SGH=P001 or prp@SGH=billing or (prp@SGH=insurance and grp@SGH=GI001)` |
