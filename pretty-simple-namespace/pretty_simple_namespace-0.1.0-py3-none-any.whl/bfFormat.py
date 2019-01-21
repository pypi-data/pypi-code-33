#
# README
#  - Per this SO post: https://stackoverflow.com/a/33704700/984407
#    ...a breadth first (bf) traversal is more easily implemented iteratively
#    as opposed to recursively.  I can attest to this because trying to turn my
#    initial recursive depth first traversal into breadth first was painful.
#
#    What makes this especially complex is the need to traverse breadth first
#    while also needing to ensure strings are inserted in the correct order.
#    That is the reason for the LinkedList, queues and callbacks.
#

# ------- #
# Imports #
# ------- #

from all_purpose_dict import ApDict
from another_linked_list import LinkedList
from all_purpose_set import ApSet
from types import SimpleNamespace as o
from .queue import Queue
import os

from .fns import (
    assignAll,
    discard,
    getListOfCollectionKeys,
    iif,
    isEmpty,
    isLaden,
    joinWith,
    map_,
    mOrder,
    passThrough,
)


# ---- #
# Init #
# ---- #

placeholder = object()
primitiveTypes = ApSet([int, float, bool, str, type(None)])


# ---- #
# Main #
# ---- #


def bfFormat(something, style):
    def bfFormat_inner(ctx, something, key=None):
        ctx.result.append(placeholder)
        leadingStr = makeLeadingStr(ctx, key)

        if ctx.refs.has(something):
            pathToRef = ctx.refs.get(something)
            insertSimpleResultWhenDone(ctx, leadingStr + f"<ref {pathToRef}>")
            return ctx

        if ctx.inArray:
            ctx.refPath[-1] = (True, key)
        elif ctx.hasKeys:
            ctx.refPath[-1] = (False, key)

        if not isPrimitive(something):
            ctx.refs.set(something, buildPathToRef(ctx.refPath))

        if isinstance(something, list):
            if isEmpty(something):
                insertSimpleResultWhenDone(ctx, leadingStr + "[]")
                return ctx

            formatQueue.add(makeFormatList(ctx, something, leadingStr))

        elif isinstance(something, o) or isinstance(something, dict):
            if isEmpty(something):
                insertSimpleResultWhenDone(ctx, leadingStr + "{}")
                return ctx

            formatQueue.add(makeFormatDict(ctx, something, leadingStr))

        elif callable(something):
            line = f"{leadingStr}{something.__name__}()"
            insertSimpleResultWhenDone(ctx, line)

        elif isinstance(something, str):
            insertSimpleResultWhenDone(ctx, f"{leadingStr}'{something}'")

        elif isinstance(something, bool):
            lowerBool = str(something).lower()
            insertSimpleResultWhenDone(ctx, leadingStr + lowerBool)

        elif something is None:
            lowerBool = str(something).lower()
            insertSimpleResultWhenDone(ctx, leadingStr + "none")

        else:
            insertSimpleResultWhenDone(ctx, leadingStr + str(something))

        return ctx

    def makeFormatRoot(ctx, something):
        def formatRoot():
            return bfFormat_inner(ctx, something)

        return formatRoot

    #
    # Yes 'Dict' includes SimpleNamespace here, I just couldn't think of a
    #   succinct term that encompassed both.  And since SimpleNamespace is
    #   pretty much a dict, this makes sense enough for me.
    #
    def makeFormatDict(ctx, aDict, leadingStr):
        nodeToInsertAt = ctx.result.lastNode
        dictCtx = createCtx(ctx, hasKeys=True)

        def formatDict():
            nonlocal dictCtx
            dictCtx = reduce(bfFormat_inner, dictCtx)(aDict)

            insertResult = makeInsertCollectionResult(
                ctx, dictCtx, nodeToInsertAt, leadingStr, isList=False
            )
            addToWhenDone(insertResult, ctx)

        return formatDict

    def makeFormatList(ctx, aList, leadingStr):
        nodeToInsertAt = ctx.result.lastNode
        listCtx = createCtx(ctx, inArray=True)

        def formatList():
            nonlocal listCtx
            listCtx = reduce(bfFormat_inner, listCtx)(aList)

            insertResult = makeInsertCollectionResult(
                ctx, listCtx, nodeToInsertAt, leadingStr, isList=True
            )
            addToWhenDone(insertResult, ctx)

        return formatList

    def createCtx(currentCtx, **kwargs):
        props = o(**kwargs)
        newCtx = assignAll.simpleNamespaces(
            [makeDefaultCtxProps(), props, style]
        )

        if currentCtx:
            newCtx.refs = currentCtx.refs
            newCtx.indentLevel = currentCtx.indentLevel + 1
            #
            # refPath holds an array of tuple pairs
            # (IsArrayIndex, key)
            #
            newCtx.refPath = currentCtx.refPath + [None]
            newCtx.refs = currentCtx.refs

        newCtx.indentStr = getIndentStr(newCtx)
        return newCtx

    def insertSimpleResultWhenDone(ctx, line):
        nodeToInsertAt = ctx.result.lastNode

        def insertSimpleResult():
            ctx.result.insertAfter(nodeToInsertAt, line)

        addToWhenDone(insertSimpleResult, ctx)

    #
    # isList will have to change if more collections are added which have
    #   different opening and closing notation
    #
    def makeInsertCollectionResult(
        ctx, nestedCtx, nodeToInsertAt, leadingStr, *, isList
    ):
        def insertCollectionResult():
            open_ = iif(isList, "[", "{")
            close = iif(isList, "]", "}")
            nestedCtx.result.prepend(leadingStr + open_)
            nestedCtx.result.append(ctx.indentStr + close)
            ctx.result.insertAllAfter(nodeToInsertAt, nestedCtx.result)

        return insertCollectionResult

    def addToWhenDone(insertResult, ctx):
        key = ctx.indentLevel
        if key not in whenDoneDict:
            whenDoneDict[key] = Queue()

        whenDoneDict[key].add(insertResult)

    rootCtx = createCtx(None, refPath=[], refs=ApDict())
    formatRoot = makeFormatRoot(rootCtx, something)
    formatQueue = Queue([formatRoot])
    whenDoneDict = {}

    while isLaden(formatQueue):
        formatFn = formatQueue.pop()
        formatFn()

    whenDoneList = toOrderedListByKey(whenDoneDict)
    for whenDoneFnQueue in whenDoneList:
        while isLaden(whenDoneFnQueue):
            whenDoneFn = whenDoneFnQueue.pop()
            whenDoneFn()

    return passThrough(
        rootCtx.result.append(""),
        [list, discard(placeholder), joinWith(os.linesep)],
    )


# ------- #
# Helpers #
# ------- #


def makeDefaultCtxProps():
    return o(inArray=False, indentLevel=0, hasKeys=False, result=LinkedList())


def toOrderedListByKey(aDict):
    return passThrough(
        aDict,
        [getListOfCollectionKeys, mOrder("desc"), map_(toValueFrom(aDict))],
    )


def toValueFrom(aDict):
    def keyToValue_inner(aKey):
        return aDict[aKey]

    return keyToValue_inner


def makeLeadingStr(ctx, key):
    keyStr = iif(ctx.hasKeys, str(key) + ": ", "")
    return ctx.indentStr + keyStr


def getIndentStr(ctx):
    return " " * ctx.indent * ctx.indentLevel


def buildPathToRef(refPath):
    result = ["root"]

    for isArrayIndex, key in refPath:
        if isArrayIndex:
            result.append(f"[{key}]")
        else:
            result.append(f".{key}")

    return "".join(result)


def reduce(fn, initial):
    def reduceInner(something):
        result = initial

        if isinstance(something, dict):
            for key, value in something.items():
                result = fn(result, value, key)

        elif isinstance(something, o):
            for key, value in something.__dict__.items():
                result = fn(result, value, key)

        elif isinstance(something, list):
            for idx, value in enumerate(something):
                result = fn(result, value, idx)

        else:
            result = fn(result, something)

        return result

    return reduceInner


def isPrimitive(something):
    return type(something) in primitiveTypes
