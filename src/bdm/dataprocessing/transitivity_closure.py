import collections

groups = collections.defaultdict(list)
group_value = 0

def flip(flag):
    if flag is True:
        return False
    else:
        return True

def transitive_closure(v1, v2):
    global group_value

    if len(groups) == 0:
        key = "group" + str(group_value)
        groups[key].append(v1)
        groups[key].append(v2)
        group_value += 1

    flagv1 = False
    flagv2 = False
    which_group = ""
    for key, value in groups.items():

        # check in every group, if not then create one
        # print(key, value)
        if v1 not in value and v2 not in value:
            flagv1 = flip(flagv1)
            flagv2 = flip(flagv2)

        elif v1 not in value and v2 in value:
            flagv1 = flip(flagv1)
            which_group = key
        elif v1 in value and v2 not in value:
            flagv2 = flip(flagv2)
            which_group = key

    if flagv1 is True and flagv2 is True:
        key = "group" + str(group_value)
        groups[key].append(v1)
        groups[key].append(v2)
        group_value += 1
    elif flagv1 is True:
        groups[which_group].append(v2)
    elif flagv2 is True:
        groups[which_group].append(v1)