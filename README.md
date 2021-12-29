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

| ID | Stakeholder | Pain Points | User Requirements | Priority |
|----|-------------|-------------|-------------------|----------|
|B1  |BMT          | The scope of a tech's work is very broad and a lot of time and value added isn't captured | Capture value
BMTs bring beyond what’s shown in WOs (e.g. training new hires, assisting clinical staff) | High | 

### Design

### Implementation Logic

### Limitations

## Getting Started

### Prerequisites

### Installation

## Usage

## Acknowledgements 
