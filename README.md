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

The goal of the stakeholder interviews was twofold:
1. Understand LMBME’s processes
2. Identify pain points working with COSR method of budgeting and managing a strapped budget

After speaking with LMBME staff, business processes were categorized into several overarching pools:

![business_processes](https://user-images.githubusercontent.com/54252001/147626748-ab9f2f77-a766-40b4-86bd-29e6f0a01a98.png)

Below is a selection of pain points that were raised during stakeholder interviews:

![stakeholder_pain_points](https://user-images.githubusercontent.com/54252001/147628717-67acdf8c-ac3f-4047-8b03-57998d15e0df.png)

<p align="right"><a href="#top">[Back to top]</a></p>

### Design
The design of the cost model was informed by the literature reviews and stakeholder interviews outlined above. Below is a diagram 
that illustrates how job-order costing was implemented for this cost model. 

![job_order_costing](https://user-images.githubusercontent.com/54252001/147630976-7be00510-34f8-4d9f-8d28-4b12ceadd452.jpg)

The goal of job-order costing is to determine how much money it costs to produce a product or service based on the direct and 
indirect (i.e. overhead) costs associated with that product or service. Direct costs are any costs that can be explicitly traced 
back to a single unit of a product or service. Indirect or overhead costs are any costs that need to be incurred in order to 
produce a product or service, but cannot be explicitly linked to a single unit of the product or service. In the case of LMBME, 
the “service” offered is the support and management of medical devices.

**Direct Costs**

Work orders (i.e. preventative maintenance, corrective work, risk management, incoming inspection, etc.) are direct costs since techs work directly on repairing and inspecting devices. This is work that can be explicitly traced back to a single asset because we can use TMS data to determine the number of support hours, and hence the service cost for any given device. Given this logic, parts and service contracts should also technically be direct costs. However, the design of this cost model lumps parts and service contract costs into overhead. The reason for this is threefold:

1. TMS parts cost data is not accurate
2. Service contract costs are not included as a field in TMS
3. Parts and service contract costs are inconsistently charged to different accounts in the Statements of Operations, making them difficult and cumbersome to separate from the indirect costs

Direct costs take care of the “Maintenance and risk management” and “End of life” business processes from the “Research” section 
since those processes are all encompassed in work orders. 

**Indirect Costs**

Whereas direct costs are determined on an asset basis, indirect costs are determined on a cost centre basis. There are three main 
pools of indirect costs: 

*Tech labour costs*

1. Based on anecdotal evidence from stakeholder interviews with LMBME technologists, ~35% of a technologist’s work was determined 
to be non-device related (i.e. time spent in meetings, speaking with clinical staff, offering input on asset procurement, 
etc.). Hence, 35% of the total tech labour cost for a cost centre is added to the cost centre overhead.
2. Indirect tech labour costs account for some of the costs in the “Planning and procurement” (i.e. purchasing) and “Training” 
(i.e. in-house education to clinical staff) business processes.

*Non-tech labour costs*

1. Non-tech staff include all LMBME staff with regional responsibilities (i.e. they oversee multiple cost centres).
2. Since non-tech LMBME staff do not work directly with devices, all of the total compensation for non-tech staff gets distributed 
as overhead to the costs centres at which the non-tech staff have oversight. Non-tech labour costs account for a wide variety
of miscellaneous indirect costs that otherwise would not be accounted for. 

*Non-labour costs*
1. Non-labour overhead costs are all the remaining costs on the Statement of Operations for a cost centre after removing labour 
costs and direct costs.
2. A lot of the miscellaneous costs such as training (sundry) and operational supplies (supplies) are accounted for here.

**POHR**

Recall that the indirect (i.e. overhead) costs outlined in the section above were identified on a cost centre basis. However, we 
need to determine the overhead cost per asset. To do this, we need to compute a pre-determined overhead rate (POHR). This is the 
estimated amount of overhead cost that should be applied to a single asset based on some cost driver. The cost driver used by this 
cost model is the number of tech labour hours—this not only logically makes sense, but labour hours is generally the standard cost
driver used in most implementations of job-order costing. What a cost driver of tech labour hours says is that we expect the 
amount of overhead incurred by a cost centre to increase if the number of tech labour hours increases. This makes sense—consider 
the possible scenarios:
1. Tech labour costs: This overhead cost pool will obviously increase—tech labour costs increase proportionally with the number of tech labour hours.
2. Non-tech labour costs: This overhead cost pool may or may not increase—at worse it will stay constant as the number of tech 
labour hours increases. If many new techs are hired in a region, maybe a new regional manager will be hired. In this case, non-
tech labour costs would increase with the number of tech labour hours.
3. Non-labour costs: This overhead cost pool will likely increase proportionally with tech labour hours. If we hire an additional 
tech at a cost centre, the cost of training, miscellaneous supplies, etc. will likely increase as well.

Hence, to compute the POHR for any given cost centre, the cost model uses the formula:

`POHR = (Tech labour costs + Non-tech labour costs + Non-labour costs) / Total tech labour hours in a year`

**Total Cost to Service an Asset**

Finally, to determine the cost to service Asset X, the cost model uses the following formula: 

`Cost to service = (POHR * WO Hours for Asset X) + (Tech Hourly Wage * WO Hours for Asset X)`

In the formula above, WO hours is the average annual number of WO hours spent supporting the asset and tech hourly wage is the 
weighted average wage for all the techs working at the cost centre where the asset is located. 

### Implementation Logic

### Limitations

## Getting Started

### Prerequisites

### Installation

## Usage

## Acknowledgements 
