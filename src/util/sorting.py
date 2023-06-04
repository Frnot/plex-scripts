# min-op sorting algo
# v1.0

# an algorithm that attempts to sort an array arbitrarily using the least number of move operations
# for this problem, moving an array element from any index n to m is considered a single operation
# other measures of time complexity are not considered

# This algorithm was developed primarily to sort a youtube playlist using the least number of API calls


def compute_sorting_ops(existing, update):
    """Takes a list of existing items and a list of updated items
    Returns a minimum list of operations required to transform <existing> into <update>"""

    ops = [] # a list of operations to perform on the existing list

    # Step 1: remove items from existing that don't exist in update
    idx = 0
    while idx < len(existing):
        if existing[idx] not in update:
            ops.append(("del", existing[idx]))
            existing.pop(idx)
        else:
            idx += 1

    # Step 2: sort existing items
    existing, operations = sort(existing, update)
    ops.extend(operations)

    # Step 3: add missing items to the correct indexes
    for idx,e in enumerate(update):
        if e not in existing:
            ops.append(("add", e, idx))
            existing.insert(idx, e)

    return existing, ops




def sort(unsorted, sorted):
    """    
    items in unsorted listed are mapped to their correct position in the sorted list
    an unsorted item's position in the sorted list is reffered to as ordval
    
    ex:
    correct order: [D, A, C, E, B]
    unsorted order: [C, B, D, A, E]
    item -> ordval
        C : 2
        B : 4
        D : 0
        A : 1
        E : 3
    """

    ops = []

    # step 1: generate ordvals
    ordval = {}
    for i in unsorted:
        ordval[i] = sorted.index(i)

    # find the largest set of in-order elements
    # unsorted and sorted should be equal sets
    sorted_lim = [i for i in sorted if i in unsorted]
    ordered = biog(None, unsorted, sorted_lim, ordval)

    # generate list of unordered elements
    unordered = [i for i in unsorted if i not in ordered]

    # sort the unordered elements, keeping track of the state of the list in the process
    while len(unordered) > 0:
        e = unordered.pop(0)
        old_idx = unsorted.index(e)
        last_se = ordered[0]

        if ordval[e] < ordval[last_se]: # beginning
            new_idx = unsorted.index(last_se)
            ops.append(("mov", e, new_idx))

            unsorted.pop(old_idx)
            unsorted.insert(new_idx, e)

            ordered.insert(0, e)
            continue

        for next_se in ordered[1:]: # middle
            if ordval[last_se] < ordval[e] and ordval[e] < ordval[next_se]:
                # sort main list
                new_idx = unsorted.index(last_se) + 1
                ops.append(("mov", e, new_idx))

                unsorted.pop(old_idx)
                if old_idx < new_idx:
                    unsorted.insert(new_idx-1, e)
                else:
                    unsorted.insert(new_idx, e)

                # update ordered list
                ordered.insert(ordered.index(last_se) + 1, e)
                break
            last_se = next_se

        else: # last
            if ordval[last_se] < ordval[e]:
                new_idx = unsorted.index(last_se) + 1
                ops.append(("mov", e, new_idx))

                unsorted.pop(old_idx)
                if old_idx < new_idx:
                    unsorted.insert(new_idx-1, e)
                else:
                    unsorted.insert(new_idx, e)

                # update ordered list
                ordered.insert(ordered.index(last_se) + 1, e)

    return unsorted, ops




def biog(initial_element, partial_list, sorted, ordval):
    """
    Finds largest set of elements that occur in order in <partial_list>
    The time complexity of this function is difficult to compute
    safe to say, it is very bad.
    """

    complete_set = set(partial_list)
    traversed = set()

    if initial_element is not None:
        groups = [[initial_element]]
        initial_ordval = ordval[initial_element]
    else:
        groups = []
        initial_ordval = -1

    while not traversed == complete_set:
        # find smallest in-order element to the right of index 0
        smallest = None
        for e in partial_list:
            if ordval[e] < initial_ordval or e in traversed:
                continue
            if smallest is None or ordval[e] < ordval[smallest]:
                smallest = e

        if smallest is None:
            break

        if partial_list.index(smallest) == len(partial_list)-1: # smallest element is at end of list
            if initial_element is not None:
                groups.append([initial_element, smallest])
            else:
                groups.append([smallest])

            traversed.add(smallest)
        else:
            group = biog(smallest, partial_list[partial_list.index(smallest)+1:], sorted, ordval)
            traversed.update(group)
            if initial_element is not None:
                group.insert(0, initial_element)
            groups.append(group)

    # return longest group
    maxidx = 0
    maxlen = 0
    for idx, group in enumerate(groups):
        if len(group) > maxlen:
            maxlen = len(group)
            maxidx = idx
    return groups[maxidx]

    





if __name__ == "__main__":
    import random
    from time import perf_counter
    from blessings import Terminal
    term = Terminal()

    size_of_array = 50
    total_exec_time = 0

    for iteration in range(1000000):
        data = [i for i in range(size_of_array)]
        random.shuffle(data)
        order = data.copy()
        random.shuffle(data)
        
        with term.location(0, term.height-3):
            print(f"Order: {order}", end='\r')
        with term.location(0, term.height-2):
            print(f"Data:  {data}", end='\r')
        
        s = perf_counter()
        sorted, ops = main(data, order)
        e = perf_counter()

        total_exec_time += e - s

        with term.location(0, term.height-1):
            print(f"iteration: {iteration+1} avg execution time: {total_exec_time/(iteration+1)}", end='\r')

        if sorted != order:
            print("Error: data sorted incorretly:")
            print(f"{data=}")
            print(f"{order=}")
            print(f"{sorted=}")
            break

    print()

    #order = ["D", "A", "C", "E", "B"]
    #order = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "", "Z"]