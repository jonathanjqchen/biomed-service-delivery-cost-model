<div id="top"></div>

## Table of Contents
1. [Lower Mainland Biomedical Engineering Service Delivery Cost Model](#lower-mainland-biomedical-engineering-service-delivery-cost-model)
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
Lower Mainland Biomedical Engineering (LMBME) is an initiative that oversees the maintenance, patient safety, education, procurement, budgeting, planning, projects, and design of medical technology across four of BC's largest health authorities—Providence Health Care, Fraser Health, Provincial Health Services, and Vancouver Coastal Health.  

The method that LMBME has traditionally used for estimating the cost to support net new devices is a simple multiplication of an asset’s acquisition cost by the cost-of-service-ratio (COSR). The biomedical engineering standard for the COSR is 5%—this ratio tells us that the approximate annual cost to support an asset is 5% of the asset’s total acquisition cost. For example, an asset with an acquisition cost of $5000 would have an estimated support cost of 0.05 * $5000 = $250.

Each year, LMBME submits budgetary pressures based on the influx of net new devices that they receive and support on top of their existing fleet of devices. Using the COSR to estimate these annual budgetary pressures is problematic for several reasons:

1. Not all devices require the same amount of work to support, so applying a flat 5% ratio to the acquisition cost of all net new devices is not an accurate reflection of the actual amount of work, and hence cost, required to support these devices.
2. Determination of the COSR (whether it is 5%, 7%, or 10%) is grounded on intuition. Although this intuition is backed by many years of biomedical engineering experience, the finance department prefers a more sophisticated and data-driven approach when it comes to justifying annual budget increases.
3. Acquisition cost data on TMS (LMBME's relational database application) is often missing or inaccurate. 

Given the above issues with the COSR method of estimating service delivery costs, the goal of this project was to develop a data-driven cost model rooted in accounting principles that could systematically estimate asset support costs.

<p align="right"><a href="#top">Back to top</a></p>

### Research

### Design

### Implementation Logic

### Limitations

## Getting Started

### Prerequisites

### Installation

## Usage

## Acknowledgements 
