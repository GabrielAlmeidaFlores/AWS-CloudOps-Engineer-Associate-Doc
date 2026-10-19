# Resource Groups

This document explains how Resource Groups turns a tag scheme into a reusable target that Systems Manager can act on, which is why it belongs in this topic even though it is not an SSM service. It covers tag-based and stack-based queries, the regional and nesting rules, and the targeting pattern; the tag syntax itself is in [16-tagging.md](16-tagging.md).

## What a resource group is

A **resource group** is a collection of AWS resources in **one AWS Region** that match a query. The group is defined by the query, not by a static list, so resources that match the criteria are members automatically.

- **Tag-based query.** Membership is based on a list of resource types and tags. This is the flexible form: tag instances with `Environment=prod` and `Layer=web`, and a group can select exactly those.
- **CloudFormation stack-based query.** Membership is based on the resources in one CloudFormation stack, optionally restricted to specific resource types within the stack.
- **Regional.** A resource group is scoped to a single Region, and its resources are declared as `AWS::service::resource`.
- **Nestable.** A group can contain other groups in the same Region, so you can build a hierarchy.
- **Service-linked.** Some services create and manage their own resource groups, which you cannot fully edit in the Resource Groups console.

## Why it matters for Systems Manager

Resource groups turn tag conventions into reusable targets:

- **Run Command and State Manager** can target a resource group instead of enumerating nodes.
- **Maintenance Windows** can target a resource group, which is how you reach nodes that are offline at the time the window is defined.
- **Application Manager** imports resources grouped by CloudFormation stacks, AppRegistry, and clusters.
- **Explorer and OpsCenter** can group and filter operational data by the tag keys you nominate (Explorer lets you set up to five reporting tag keys).

The practical rule: define your tag schema first (for example `Environment`, `Layer`, `PatchGroup`), then build resource groups on top of it, then target Systems Manager operations at the group. Changing the tag membership changes the target set with no document edits. The tag rules themselves (key/value case sensitivity, the 50-tag cap, the `Patch Group` key, and IAM tag conditions) are in [16-tagging.md](16-tagging.md).

The Resource Groups console lists the groups in the current Region. The screenshot below shows two groups in the sandbox account, named by environment.

![Resource Groups console listing two environment groups](../../../assets/images/screenshots/ssm/06-resource-groups-list.png)

*The Resource Groups console. The two groups, `dev_team_instance` and `prd_team_instance`, are named by environment and owned by the account; Create resource group starts a new one. Both sit in the same Region, which is the scope a resource group is limited to.*

Opening a group shows how its membership is defined, which is the part that matters for targeting. The configuration screen below shows `dev_team_instance` as a tag-based query: the resource type `AWS::EC2::Instance` and the tag `Environment: DEV`.

![Resource group configuration showing a tag-based query for EC2 instances tagged Environment=DEV](../../../assets/images/screenshots/ssm/22-resource-groups-config.png)

*The group configuration for `dev_team_instance`. Label 1 marks the tag-based query type, label 2 the resource type, and label 3 the tag that defines membership. Label 4 marks the member list, which currently holds one instance, `WEBSERVER-SANDBOX`; membership is computed from the query, not maintained by hand, so retagging an instance moves it in or out of the group with no query edit.*

## Example

Create a tag-based group for production web servers and list its members:

```bash
# Group production web-tier instances by tags
aws resource-groups create-group \
  --name prod-web \
  --resource-query '{"Type":"TAG_FILTERS_1_0","Query":"{\"ResourceTypeFilters\":[\"AWS::EC2::Instance\"],\"TagFilters\":[{\"Key\":\"Environment\",\"Values\":[\"prod\"]},{\"Key\":\"Layer\",\"Values\":[\"web\"]}]}"}'

# List the resources currently in the group
aws resource-groups list-group-resources --group-name prod-web
```

## Limits and an exam note

The limits below decide how far a tag-based grouping scheme can scale, and one of them is regional: a group cannot span Regions, so a multi-Region fleet needs a group per Region even when the tags are identical.

- **Resource groups per account per Region:** 100 by default (adjustable). A large tag-based scheme can exceed it, and the fix is a quota increase rather than splitting the query.
- **Tags per resource:** 50 user-created tags; a tag key is 1 to 128 characters, and keys beginning with `aws:` are reserved. The cap is per resource, and a resource at the cap rejects the next tag.
- **Regional, always.** A resource group cannot span Regions, so a fleet that runs in three Regions needs three groups even when the tag values are identical. A scenario that expects one group to cover every Region is testing exactly this.

## Sources

The references below are the official AWS pages behind the behavior and numbers in this document; use them when a value or rule needs checking against the source.

- AWS: *What are resource groups?*. https://docs.aws.amazon.com/ARG/latest/userguide/resource-groups.html
- AWS: *AWS services that work with AWS Resource Groups*. https://docs.aws.amazon.com/ARG/latest/userguide/integrated-services-list.html
- AWS: *AWS Resource Groups and Tagging endpoints and quotas*. https://docs.aws.amazon.com/general/latest/gr/arg.html
