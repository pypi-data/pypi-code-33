from __future__ import absolute_import

from mercurial import (
    error,
    registrar,
    revset,
    util,
)

from . import (
    destination,
    stack,
)

try:
    mkmatcher = revset._stringmatcher
except AttributeError:
    try:
        from mercurial.utils import stringutil
        mkmatcher = stringutil.stringmatcher
    except (ImportError, AttributeError):
        mkmatcher = util.stringmatcher

revsetpredicate = registrar.revsetpredicate()

def getstringstrict(x, err):
    if x and x[0] == 'string':
        return x[1]
    raise error.ParseError(err)

@revsetpredicate('topic([string or set])')
def topicset(repo, subset, x):
    """All changesets with the specified topic or the topics of the given
    changesets. Without the argument, all changesets with any topic specified.

    If `string` starts with `re:` the remainder of the name is treated
    as a regular expression.
    """
    args = revset.getargs(x, 0, 1, 'topic takes one or no arguments')

    mutable = revset._notpublic(repo, revset.fullreposet(repo), ())

    if not args:
        return (subset & mutable).filter(lambda r: bool(repo[r].topic()))

    try:
        topic = getstringstrict(args[0], '')
    except error.ParseError:
        # not a string, but another revset
        pass
    else:
        kind, pattern, matcher = mkmatcher(topic)

        if topic.startswith('literal:') and pattern not in repo.topics:
            raise error.RepoLookupError("topic '%s' does not exist" % pattern)

        def matches(r):
            topic = repo[r].topic()
            if not topic:
                return False
            return matcher(topic)

        return (subset & mutable).filter(matches)

    s = revset.getset(repo, revset.fullreposet(repo), x)
    topics = {repo[r].topic() for r in s}
    topics.discard('')

    def matches(r):
        if r in s:
            return True
        topic = repo[r].topic()
        if not topic:
            return False
        return topic in topics

    return (subset & mutable).filter(matches)

@revsetpredicate('ngtip([branch])')
def ngtipset(repo, subset, x):
    """The untopiced tip.

    Name is horrible so that people change it.
    """
    args = revset.getargs(x, 1, 1, 'ngtip takes one argument')
    # match a specific topic
    branch = revset.getstring(args[0], 'ngtip requires a string')
    if branch == '.':
        branch = repo['.'].branch()
    return subset & revset.baseset(destination.ngtip(repo, branch))

@revsetpredicate('stack()')
def stackset(repo, subset, x):
    """All relevant changes in the current topic,

    This is roughly equivalent to 'topic(.) - obsolete' with a sorting moving
    unstable changeset after there future parent (as if evolve where already
    run).
    """
    err = 'stack takes no arguments, it works on current topic'
    revset.getargs(x, 0, 0, err)
    topic = None
    branch = None
    if repo.currenttopic:
        topic = repo.currenttopic
    else:
        branch = repo[None].branch()
    return revset.baseset(stack.stack(repo, branch=branch, topic=topic)[1:]) & subset

if util.safehasattr(revset, 'subscriptrelations'):
    def stackrel(repo, subset, x, rel, n, order):
        """This is a revset-flavored implementation of stack aliases.

        The syntax is: rev#stack[n] or rev#s[n]. Plenty of logic is borrowed
        from topic._namemap, but unlike that function, which prefers to abort
        (e.g. when stack index is too high), this returns empty set to be more
        revset-friendly.
        """
        s = revset.getset(repo, revset.fullreposet(repo), x)
        if not s:
            return revset.baseset()
        revs = []
        for r in s:
            topic = repo[r].topic()
            if topic:
                st = stack.stack(repo, topic=topic)
            else:
                st = stack.stack(repo, branch=repo[r].branch())
            if n < 0:
                st = list(st)[1:]
            else:
                st = list(st)
            try:
                rev = st[n]
            except IndexError:
                continue
            if rev == -1 and n == 0:
                continue
            if rev not in revs:
                revs.append(rev)
        return subset & revset.baseset(revs)

    revset.subscriptrelations['stack'] = stackrel
    revset.subscriptrelations['s'] = stackrel

    def topicrel(repo, subset, x, rel, n, order):
        ancestors = revset._ancestors
        descendants = revset._descendants
        subset = topicset(repo, subset, x)
        if n <= 0:
            n = -n
            return ancestors(repo, subset, x, startdepth=n, stopdepth=n + 1)
        else:
            return descendants(repo, subset, x, startdepth=n, stopdepth=n + 1)

    revset.subscriptrelations['topic'] = topicrel
    revset.subscriptrelations['t'] = topicrel
