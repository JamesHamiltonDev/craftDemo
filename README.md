# Level 1 Craft Demo

Your team is moving from 2 corporate data centers to a public cloud provider. You have picked up the following User Story from the team's backlog:

### User Story

As a DevOps Engineer, I need to know how many applications we are hosting in our two corporate data centers so the team can start planning the migration to AWS

### Acceptance Criteria:
* Data must be pulled from Excel file embedded in this GitHub repo, hardware.xlsx.
* Data must be parsed using either Go (preferred) or Python.
* Application/script should generate a list of all departments that have hardware hosted.
* Application/script should generate a list of all the applications for each department.
* Application/script should calculate the number of CPUs and memory used by each department.
* Application/script should calculate the number of CPUs and memory used by each application.
* Application/script should calculate the number of CPUs and memory used in each of the data centers.
* Application/script should be completed by sending a pull request to the master branch.


# Level 2 Craft Demo

Your last story has allowed the team to determine how much infrastructure needs to be moved to the new cloud provider. The finance department has just called and wants to know how much this cloud migration will affect the hosting costs budget over the next 3 years. You have a new User Story to extend the application/script from level 1:

### User Story

As a DevOps Engineer, I need to know how the cloud migration will impact our 3 year hosting budget forecast so the finance team can plan for the changed costs.

### Acceptance Criteria:
* You only have to forecast EC2 on-demand instance costs using the public AWS price list: https://aws.amazon.com/ec2/pricing/on-demand/.
* You can assume that the EC2 price list will *not* change for 3 years.
* You can assume that we will *not* resize any hardware during the migration.
* You can assume that each instance will be *RHEL-based* and will run 24/7/365.
* The Engineering team has forecasted hardware growth of 10% in Year 1, 25% in Year 2 and 40% in Year 3.
* The Sales team is moving to managed services and has forecasted that their hardware needs will reduce by 80% in Year 1 and 100% in Year 2.
* Application/script should calculate hosting costs for each department for Year 1, Year 2 and Year 3.
* Application/script should be completed by sending a pull request to the master branch.
