# Known Issues - BackyardLeadAI

This document tracks current issues with the BackyardLeadAI application, including root causes, impacts, and proposed fixes.

## Issue 1: Small Backyards Misclassified as Undeveloped
- **Description**: Some properties with very small but partially landscaped backyards are classified as `undeveloped`, inflating the number of “high‑potential” leads.  
- **Root Cause**: The vision prompt and model are optimized for clear, large backyard areas and may over‑weight bare patches or shadows in small lots.  
- **Impact**: Landscaping companies may receive a subset of leads that are less attractive or lower value than expected.  
- **Proposed Fixes**:  
  - Refine the OpenAI Vision prompt to better distinguish small decorative areas from truly undeveloped space.  
  - Introduce a minimum `lotSize` and/or `backyard_area` threshold in the lead scoring logic.  
  - Add a tunable “small lot penalty” parameter in config and expose it via environment variables.  
- **Status**: Open  
- **Priority**: High  

## Issue 2: Imagery Staleness for Newly Developed Backyards
- **Description**: Satellite images may not reflect recent landscaping work, causing some fully developed yards to appear `undeveloped` or `partially_developed`.  
- **Root Cause**: Imagery providers cache tiles and update them infrequently; there is no guarantee of recency for every neighborhood.  
- **Impact**: Some leads may already have completed backyard projects, reducing close rates for landscaping offers.  
- **Proposed Fixes**:  
  - Document this limitation clearly in marketing and product copy.  
  - Explore using multiple imagery providers where allowed to improve freshness.  
  - Add an optional “imagery_age_hint” field when provider metadata is available.  
- **Status**: Open  
- **Priority**: Medium  

## Additional Notes
- These issues will be revisited after initial pilots with landscaping customers.  
- Review and update this file as fixes are implemented and new issues are discovered.  
- Last Updated: [Current Date]  