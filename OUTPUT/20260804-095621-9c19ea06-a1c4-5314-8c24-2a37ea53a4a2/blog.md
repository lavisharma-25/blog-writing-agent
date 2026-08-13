# How to Create and Launch an AWS EC2 Instance A Step-by-Step Guide from Start to Finish

### Prerequisites: AWS Account, IAM User, and CLI Setup

Start with a valid AWS account that you can access as the root user. For day-to-day work, do **not** use root credentials. Instead, sign in as root, navigate to IAM, and create an IAM user with both console access and programmatic access (access key ID and secret access key). Attach a scoped policy such as `AmazonEC2FullAccess`, or better, a custom policy limited to the EC2, CloudWatch, and key-pair operations you need. Least privilege is the goal, and you can tighten permissions later.

Enable MFA on the IAM user immediately. Store the access keys in a secure location such as a password manager or an encrypted file, and never commit them to source control.

Next, install AWS CLI v2 from the official AWS page. After installation, run:

```bash
aws configure
```

Enter your access key ID, secret access key, a default region such as `us-east-1`, and output format `json`. If you have multiple profiles, use `--profile` to keep them isolated.

Before launching an instance, confirm that your default network is present in the chosen region. Default VPCs and subnets are usually created automatically, but verify with:

```bash
aws ec2 describe-vpcs
aws ec2 describe-subnets
```

If no default VPC exists, create one or select a custom VPC later in the launch wizard.

Finally, create an AWS Budgets billing alert to monitor EC2 spend from day one. Set a low monthly threshold and configure email alerts so unexpected usage does not turn into an expensive surprise. With IAM credentials, CLI access, a valid VPC, and a budget in place, you are ready to launch your EC2 instance.

## Select the Right AMI and Instance Type

In the EC2 console launch instance wizard, keep the **Quick Start** tab active and select an **Amazon Linux 2023** AMI. This is a stable x86_64 image, and Amazon Linux 2023 is a common free-tier-eligible option for new instances. ([Source](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EC2_GetStarted.html)) ([Source](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-launch-instance-wizard.html))

Avoid hard-coding an AMI ID into scripts, because AMIs are updated regularly. With AWS CLI v2, you can query the latest Amazon Linux 2023 x86_64 AMI:

```bash
aws ec2 describe-images --owners amazon \
  --filters 'Name=name,Values=al2023-ami-2023.*-x86_64' \
  --query 'Images[*].[ImageId,CreationDate]' --output table
```

The output shows the newest `ImageId` and its creation date. Use that ID when you launch from the CLI, and always confirm that the AMI still exists in your target region. ([Source](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EC2_GetStarted.html))

Next, choose an instance type. For free-tier-oriented workloads, compare `t2.micro`, `t3.micro`, and `t4g.micro`. The last one is ARM-based and may offer a different price/performance balance than the x86_64 `t` series. Free tier eligibility and instance availability vary by region and change over time, so verify the current terms before you launch. ([Source](https://aws.amazon.com/ec2/getting-started))

Instance type names follow a readable convention. For example, `t3.micro` breaks down as:

- `t` — instance family: general purpose
- `3` — generation
- `micro` — size

Common families include `t`/`m` for general purpose, `c` for compute, `r` for memory, and `i` for storage-heavy workloads. Each size also specifies vCPUs and memory, so match those numbers to the requirements of your application. ([Source](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/EC2_GetStarted.html))

Finally, in **Configure storage**, keep the default 8 GiB gp3 root volume unless your HTTP server or build process needs more space. If your application writes persistent data, add a separate EBS volume rather than relying only on the root volume, so you can replace or snapshot data independently. ([Source](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-launch-instance-wizard.html))

## Set Up a Key Pair and Security Group

Before launching the instance, create an SSH key pair. You can do this in the AWS Console under **EC2 > Key Pairs**, or from the AWS CLI v2 with:

```bash
aws ec2 create-key-pair \
  --key-name my-key \
  --key-type ed25519 \
  --query 'KeyMaterial' \
  --output text > ~/.ssh/my-key.pem

chmod 400 ~/.ssh/my-key.pem
```

The `chmod 400` step is required on Linux/macOS; otherwise SSH will refuse to use the key.

Treat the private key file like a password. AWS never lets you download it again after creation. If you lose it, you cannot recover it from AWS; you will need to create a new key pair.

You must attach this key pair at launch. Without it, you cannot SSH into a Linux instance from outside. Select your key pair in the launch instance wizard before starting the instance.

Next, create a security group named `ssh-only`. This acts as your instance firewall. Add exactly one inbound rule:

- **Type:** SSH
- **Protocol:** TCP
- **Port:** 22
- **Source:** your current public IP with `/32`, for example `203.0.113.10/32`

Do not use `0.0.0.0/0`. That would allow every IP address on the internet to attempt SSH connections to your instance. Restricting the source to your own IP is a least-privilege approach and reduces brute-force risk.

Leave outbound traffic as the default allow-all for now. Avoid opening ports such as 80 or 443 unless you are intentionally hosting a public service. Every open port is an additional attack surface, so start with the smallest access you need.

## Launch the Instance and Confirm Status Checks

Once you’ve verified the AMI, instance type, key pair, security group, and storage, you can start the instance. In the launch wizard, click **Launch Instance**. If you prefer the command line, you can launch the same free-tier eligible Amazon Linux 2023 instance with the AWS CLI v2:

```bash
aws ec2 run-instances \
  --image-id <ami-id> \
  --instance-type t3.micro \
  --key-name my-key \
  --security-group-ids <sg-id> \
  --subnet-id <subnet-id> \
  --associate-public-ip-address
```

- After you submit the request, the instance state moves from `pending` to `running`. Launching is not instant, so give it a few seconds.
- If you see an `insufficient-capacity` error, the selected Availability Zone does not currently have capacity for the instance type. Try a different Availability Zone or a different instance type, then repeat the launch.

Before you attempt SSH, wait for both status checks to pass. In the console, select your instance and open the **Status checks** tab. You need to see:

- **System reachability**: 2/2 checks passed
- **Instance reachability**: 2/2 checks passed

These checks verify that the underlying host is healthy and that the operating system has booted properly. SSH will usually fail until both are green.

Next, record the public IPv4 address. You can find it in the console under the **Description** tab, or retrieve it with:

```bash
aws ec2 describe-instances \
  --instance-ids <instance-id> \
  --query 'Reservations[0].Instances[0].PublicIpAddress' \
  --output text
```

If the instance enters `terminated` immediately after launch, something went wrong during initialization. Check the **Description** tab for the termination reason, then open **Actions → Monitor and troubleshoot → Get system log** to see the actual console output. Common causes include:

- A failed user-data script
- An invalid or expired AMI ID
- Missing EC2 permissions for the IAM role attached to the instance

Fixing these issues before relaunching will save you time and avoid unnecessary billing surprises.

## Connect to the Instance Using SSH or EC2 Instance Connect

Once your EC2 instance is running, the next step is opening a secure shell session. The simplest way is to SSH from your local machine.

Open a terminal and run:

```bash
chmod 400 ~/.ssh/my-key.pem
ssh -i ~/.ssh/my-key.pem ec2-user@<public-ip>
```

Replace `<public-ip>` with the public IPv4 address shown in the EC2 console. The default user name for Amazon Linux is `ec2-user`; for Ubuntu AMIs it is `ubuntu`. If you use a different AMI, check that vendor’s documentation for the correct default user.

If you do not want to handle a private key on your local machine, use EC2 Instance Connect from the AWS console. Select the instance, click **Connect**, then choose the **EC2 Instance Connect** tab. AWS opens a browser-based terminal and injects a temporary key into the instance, so you never have to download or manage the private key locally.

If you rely on SSH agent forwarding, make sure the key is loaded into your local agent:

```bash
ssh-add ~/.ssh/my-key.pem
```

After that, you can include `-A` in your SSH command when needed.

SSH errors are usually easy to diagnose.

If you see `Permission denied (publickey)`, check:

- The key file permissions are `400`. Fix with `chmod 400 ~/.ssh/my-key.pem`.
- The key pair name at launch matches the `.pem` file you are using.
- You are using the correct user name for the AMI, such as `ec2-user` or `ubuntu`.

If the connection times out, confirm:

- The instance security group allows inbound SSH on port 22 from your current public IP.
- The instance has a public IP address and is in a public subnet with an internet gateway.

Finally, if you want to connect without opening port 22 at all, enable AWS Systems Manager Session Manager. Amazon Linux 2023 includes the SSM agent, but the instance needs an IAM role with SSM permissions. Once configured, you can open a shell directly from the console without any inbound SSH rule.

## Harden and Monitor the Running Instance

Launching an instance is not the finish line. Take time to patch, restrict metadata access, and set up monitoring before relying on the instance.

### Install Patches and Plan Maintenance

Amazon Linux 2023 uses `dnf` as its package manager. After your first SSH session, run a full update:

```bash
sudo dnf update -y
```

Do not stop there. Ad-hoc patching is easy to forget. Schedule recurring maintenance windows using AWS Systems Manager Maintenance Windows or a simple cron job to apply security updates on a predictable cadence.

### Require IMDSv2

AWS provides two versions of the instance metadata service. IMDSv1 is disabled by default in newer accounts, but you should explicitly enforce IMDSv2 to block SSRF-style attacks. You can require it at launch under **Metadata options**, or enforce it on an existing instance:

```bash
aws ec2 modify-instance-metadata-options \
  --instance-id i-1234567890abcdef0 \
  --http-tokens required \
  --http-endpoint enabled
```

With IMDSv2, the instance must use a session token to access metadata, which prevents unauthenticated requests from reaching the service.

### Watch CPU and Status Checks

A runaway process can quietly consume all of your instance’s CPUs and inflate your bill. Create a CloudWatch alarm that triggers when `CPUUtilization` exceeds 80% for 10 consecutive minutes. In the **CloudWatch** console, choose **Alarms > All alarms > Create alarm**, select the instance metric, set the threshold and period, and configure the alarm to send a notification to an SNS topic with your email address subscribed.

Also create a second alarm for `StatusCheckFailed`. This metric catches both system checks, like loss of network connectivity or hardware issues, and instance checks, like kernel panic or misconfigured networking.

### Tag for Resource Management

Finally, tag your instance with at least `Name`, `Environment`, and `CostCenter`. Tags make it easy to group resources, filter billing reports, and identify ownership in shared accounts.

## Stop, Terminate, and Clean Up to Avoid Unnecessary Charges

EC2 charges do not stop just because you finished a session. You must decide whether to pause the instance or remove it entirely.

When you only need a break, choose **Stop** in the EC2 console. This preserves your EBS volume and instance state, so you can start it again later. However, stopping is not free: storage costs for the EBS volume continue, and if the instance has an associated public IP address, you may still be billed for it while the instance is stopped.

To remove the instance permanently, choose **Terminate** in the console, or use the AWS CLI:

```bash
# Pause work without deleting resources
aws ec2 stop-instances --instance-ids <instance-id>

# Remove the instance permanently
aws ec2 terminate-instances --instance-ids <instance-id>
```

If the root volume was configured with "Delete on termination" (the default), terminating the instance also deletes that volume.

Next, clean up chargeable storage. Release any Elastic IP addresses you allocated and delete unattached EBS volumes and snapshots. Even after termination, orphaned volumes and snapshots continue to generate storage charges.

After the instance is gone, delete the key pair and security group you created, but only after confirming no other instances in the same region use them. You can verify this under **Network & Security** in the EC2 console.

Finally, open the **AWS Billing dashboard** and use **Resource Groups & Tag Editor** to confirm no orphaned EC2 resources remain in the region. A quick check now will prevent a surprising bill next month.
