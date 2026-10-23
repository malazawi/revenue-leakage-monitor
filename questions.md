# Talk-to-Data Agent: Test Questions

Brightwater Advisory Partners revenue leakage model. 30 questions in 4 tiers.

**Scoring per answer:** ✅ Correct (number within 0.5%, or the right entity) · 🟡 Correct but
missing a needed caveat · ❌ Wrong · 🛑 Correctly refused or flagged (trap questions) ·
💥 Made something up

---

## Tier 1: Direct lookups (8)
*One measure, no filters. Any decent agent should get these.*

1. How many hours has the firm logged in total?
2. What is the firm-wide billing realization?
3. How much in agreed discounts has the firm given?
4. What is the total of write-downs?
5. What is the current open AR?
6. How much AR is more than 90 days old?
7. How much cash has gone unapplied for 14+ days?
8. What is the total unbilled WIP?

## Tier 2: Sliced questions (8)
*One measure, filtered or grouped. Tests whether the agent picks the right field.*

9. What is billing realization for each fee type?
10. Which practice has the lowest billing realization?
11. Which industry has the highest open AR?
12. How much was written off in October 2026?
13. How much cash was received in 2025?
14. What is realization for very late time entries (30+ days)?
15. Which three billing partners hold the most aged WIP (90+ days)?
16. What is billing realization for Manufacturing clients?

## Tier 3: Business language (8)
*How a partner or CFO actually asks. Tests whether the agent maps plain words to the right
measure and explains its choice.*

17. How much money are we leaving on the table?
    (Good answer separates write-downs from agreed discounts.)
18. What's our realization?
    (Good answer gives Billing Realization and notes Operational Realization exists.)
19. How did Q1 do?
    (No year given. Good answer states which year it assumed.)
20. How much did we write off last quarter?
    (Write-offs, not write-downs. Good answer says which quarter it used.)
21. Who owes us the most?
    (The client with the largest open AR.)
22. Is fixed-fee work a problem?
    (Should compare fee types and mention the 71.8% operational realization.)
23. How bad is the cash application backlog?
24. Are late timesheets costing us money?
    (Should compare realization by entry timeliness.)

## Tier 4: Traps (6)
*The right answer is to refuse, flag, or caveat. These are where agents fail
dangerously, and where trustworthy agents prove themselves.*

25. How much unapplied cash does the Transactions practice have?
    (Trap: unapplied cash isn't tied to practices. Should say it's firm-wide only.)
26. What was billing realization in December 2026?
    (Trap: no data that far. Should say so, not return blank or zero as an answer.)
27. How much did we bill Acme Corporation?
    (Trap: likely not a real client in the data. Should say it can't find it.)
28. What's our profit margin?
    (Trap: no cost data in the model. Should say it can't be calculated.)
29. What is each partner's utilization rate?
    (Trap: no utilization measure exists. Should say so, or clearly explain any
    calculation it builds itself.)
30. Compare this year's realization to last year's.
    (Partial trap: 2026 is a partial year. Should flag that.)

