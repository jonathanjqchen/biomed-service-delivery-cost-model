<div id="top"></div>

## Table of Contents
1. [Background](#background)
    1. [Research](#research)
    2. [Design](#design)
    3. [Implementation Logic](#implementation-logic)
    4. [Limitations](#limitations)
2. [Getting Started](#getting-started)
    1. [Prerequisites](#prerequisites)
    2. [Installation](#installation)
3. [Usage](#usage)
4. [Acknowledgements](#acknowledgements)

## Background
Lower Mainland Biomedical Engineering (LMBME) is an initiative that oversees the maintenance, patient safety, education,
procurement, budgeting, planning, projects, and design of medical technology across four of BC's largest health authorities
Providence Health Care, Fraser Health, Provincial Health Services, and Vancouver Coastal Health.  

The method that LMBME has traditionally used to estimate the cost of supporting net new devices is a simple multiplication of an
asset’s acquisition cost by the cost-of-service-ratio (COSR). The biomedical engineering standard for the COSR is 5%—this ratio
tells us that the approximate annual cost to support an asset is 5% of the asset’s total acquisition cost. For example, an asset
with an acquisition cost of $5000 would have an estimated support cost of 0.05 * $5000 = $250.

Each year, LMBME submits budgetary pressures based on the influx of net new devices that they receive and support on top of their
existing fleet of devices. Using the COSR to estimate these annual budgetary pressures is problematic for several reasons:

1. Not all devices require the same amount of work to support, so applying a flat 5% ratio to the acquisition cost of all net new devices is not an accurate measure of the actual amount of work, and hence cost, required to support these devices.
2. Determination of the COSR (whether it is 5%, 7%, or 10%) is grounded on intuition. Although this intuition is backed by many years of biomedical engineering experience, the finance department prefers a more sophisticated and data-driven approach when it comes to justifying annual budget increases.
4. Acquisition cost data on TMS (LMBME's relational database application) is often missing or inaccurate. 

Given the above issues with the COSR method of estimating service delivery costs, the goal of this project was to develop a data-driven cost model rooted in accounting principles that could systematically estimate asset support costs.

<p align="right"><a href="#top">[Back to top]</a></p>

### Research
Two research methods were used to obtain the necessary information to construct the cost model: literature reviews and stakeholder interviews.

**Literature Reviews**
The conclusion arrived at from reading through biomedical engineering journal articles is that there is no established method for
estimating service delivery costs, aside from the COSR—with a 5% COSR being the standard. Variance from the 5% standard can be
attributed to variables such as the presence of medical imaging and laboratory equipment (more expensive to support than clinical
devices), the size of the biomedical engineering department, and the type of hospital (teaching institutions tend to have higher
COSR).

The business literature consumed was centered on cost accounting. Cost accounting is a type of managerial accounting that is used
to compute the total cost of producing a product or offering a service by assessing different types of costs (fixed vs. variable,
direct vs. indirect, product vs. period, etc.). In particular, several journal articles referenced for this project discuss the
theory and application of a costing method called time-driven activity-based costing (TDABC). This is a modified version of
another popular costing method called activity-based costing (ABC), in which an organization identifies all of their business
processes (i.e. “activities”) and assigns the cost of each of these processes to a product or service based on the
consumption of that business process by the product or service. The type of costs that TDABC and ABC both focus on are direct and
indirect (i.e. overhead) costs. Significantly, TDABC has been applied successfully in hospital settings to determine the cost of
delivering different types of clinical services. Initially, the idea was to base the LMBME Service Delivery Cost Model on TDABC.
However, given the scope and the time constraints on this project, the decision was made to base the cost model on a watered-down
version of TDABC and ABC: job-order costing. Job-order costing is one of the two types of traditional costing methods and is
widely used across all industries because it is not resource-intensive to implement.

**Stakeholder Interviews**
The goal of the stakeholder interviews was two-fold:
1. Understand LMBME’s processes
2. Identify pain points working with COSR method of budgeting and managing a strapped budget

After speaking with LMBME staff, business processes were categorized into several overarching pools:

![image](https://user-images.githubusercontent.com/54252001/147626748-ab9f2f77-a766-40b4-86bd-29e6f0a01a98.png)

Below is a selection of pain points that were raised during stakeholder interviews:

| ID | Stakeholder | Pain Points | Requirement | Priority |
|----|-------------|-------------|-------------|----------|
| B1 | BMT | The scope of a tech's work is very broad and a lot of time and value added isn't captured | Capture value BMTs bring beyond what’s shown in WOs (e.g. training new hires, assisting clinical staff) | High |
| B4 | BMT | Techs aren't receiving formal training at the same rate that devices are innovating and becoming more complex | Increase training budget because techs working on high-acuity equipment should be trained by OEM, not other techs | Med |
| A1 | Admin | Dollar value of admin work isn't captured | Capture intangible value added of admin (e.g. triage calls, emails,
requests to minimize a tech’s nondevice hours) | High |
| D1 | DI | DI doesn’t deal with a lot of net new equipment, so increasing service costs may not be reflected in net new cost 
pressures | N/A | Out of scope |
| D4 | DI | DI tech apprenticeship training costs are covered by parts budget or training credits where possible | Budgeting for DI training costs | Med |
| M1 | Management | Parts, staff, training for DI is a lot more expensive than for clinical | Account for higher DI equipment costs | Med |
| M3 | Management | Service costs tend to increase with the age of devices | Data-driven approach to capturing the influence of age on ownership costs | Out of scope |
| M5 | Management | No strict training requirements to maintain vast majority of devices, so the training threshold varies from
site to site based on supervisor’s discretion | Section off a standardized training budget | Med |
| M7 | Management | Not all sites are funded equally; certain sites work with very tight budgets and struggle to free up labour to
do more work | Model should output a budget that elevates existing budget for sites that are strapped for money | High |
| M8 | Management | Not all sites have FTE techs working there every day; a tech from nearby hospital needs to travel there on 
rotation to perform maintenance activities and provide on-demand service as needed | Account for travel, accommodation, and time 
costs for these travelling techs | High |
| T1 | Training Coordinator | Training “budget” is handled differently by each HA—no standardization. Many techs feel like they 
aren’t adequately trained to perform some of their duties | Budget for at least 2 people trained on a critical device per site | Out of scope |
| T1 | Training Coordinator | Training needs on devices are recurring due to factors such as relocation, retirement, career
change, recertification requirements, large new equipment purchases, etc. | Account for the need to train up to 3-4 techs on a 
device over the course of its useful life | Out of scope |
| T1 | Training Coordinator | Sometimes techs feel like they don’t have formal training in skills that are necessary to do their
work, but aren’t directly related to maintaining devices (e.g. computer skills, networking skills, etc.) | Nice-to-have: 
Additional budget for an annual stipend for continuing education for techs | Out of scope |

### Design

### Implementation Logic

### Limitations

## Getting Started

### Prerequisites

### Installation

## Usage

## Acknowledgements 
