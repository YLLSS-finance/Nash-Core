# Nash Core Order Matching Protocol
## Introduction
The order matching protocol for Nash Core is designed to facilitate both binary- and multi-outcome markets in conditions of low liquidity probably during our initial operations, and prohibit naively exploitable arbitrage conditions from forming. It is engineered to almost be as fast as a single two-sided Limit Order Book while offering the above improvements.  
A naively exploitable arbitrage condition, in a market where the sum of the resolution value of all associated contracts shall be N, is when the sum of all Best Offers are below N or the sum of all Best Bids are above N, such that a trader may purchase the same quantity of YES or NO contracts for all outcomes and ensure a risk-free profit.

## Operation Principle
