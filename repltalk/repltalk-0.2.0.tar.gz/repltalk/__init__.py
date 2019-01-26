import aiohttp

# bots approved by the replit team that are allowed to log in
whitelisted_bots = {
	'repltalk'
}

base_url = 'https://repl.it'

class NotWhitelisted(Exception):pass
class BoardDoesntExist(Exception):pass

board_ids = {
	'share': 3,
	'ask': 6,
	'announcements': 14,
	'challenge': 16,
	'learn': 17
}

class Comment():
	def __init__(
		self, client, id, body, time_created, can_edit, can_comment, can_report, has_reported, url, votes, can_vote, has_voted, user, post, comments
	):
		self.client = client
		self.id = id
		self.content = body
		self.time_created = time_created
		self.can_edit = can_edit
		self.can_comment = can_comment
		self.can_report = can_report
		self.has_reported = has_reported
		self.url = url
		self.votes = votes
		self.can_vote = can_vote
		self.has_voted = has_voted
		self.user = user # TODO: Turn this into a User object
		self.post = post # TODO: turn this into a Post object
		self.replies = comments # TODO: turn this into a list of CommentReply objects
	def __repr__(self):
		if len(self.content) > 100:
			return repr(self.content[:100] + '...')
		else:
			return repr(self.content)

class Board():
	def __init__(self, client):
		self.client = client
	
	async def _get_posts(self):
		# print(self.client)
		if self.name == 'all':
			return await self.client._get_all_posts(
				order='new', search_query=''
			)
		else:
			if self.name in board_ids:
				board_id = board_ids[self.name]
				return await self.client._posts_in_board(
					board_id=board_id, # :ok_hand:
					order='new',
					search_query=''
				)
			else:
				raise BoardDoesntExist(f'Board "{self.name}" doesn\'t exist.')

	
	async def get_posts(self):
		_posts = await self._get_posts()
		posts = []
		for p in _posts['items']:
			show_hosted = False
			if 'showHosted' in p:
				show_hosted = p['showHosted']
			if 'board' in p:
				board = p['board']
			else:
				board = self.name
			posts.append(
				Post(
					self.client,
					p['id'],
					p['title'],
					p['body'],
					show_hosted,
					p['id'],
					board
				)
			)
		return posts

class Post():
	def __init__(
		self, client, _id, title, body, show_hosted, board, repl
	):
		self.client = client
		self.id = _id
		self.title = title
		self.body = body
		self.show_hosted = show_hosted
		self.board = board
		self.repl = repl
	
	def __repr__(self):
		return f'<{self.title}>'
	
	def __eq__(self, post2):
		return self.id == post2.id
	
	def __ne__(self, post2):
		return self.id != post2.id

	async def get_comments(self, order='new'):
		_comments = await self.client._get_comments(
			self.id,
			order
		)
		comments = []
		for c in _comments['comments']['items']:
			comments.append(Comment(
				self.client,
				id=c['id'],
				body=c['body'],
				time_created=c['timeCreated'],
				can_edit=c['canEdit'],
				can_comment=c['canComment'],
				can_report=c['canReport'],
				has_reported=c['hasReported'],
				url=c['url'],
				votes=c['voteCount'],
				can_vote=c['canVote'],
				has_voted=c['hasVoted'],
				user=c['user'],
				post=c['post'],
				comments=c['comments']
			))
		# TODO: convert this list to a list of Comment objects
		return comments

class User():
	def __init__(
		self, client, id, username, avatar, url, cycles
	):
		self.client = client
		self.id = id
		self.username = username
		self.avatar = avatar
		self.url = base_url + url
		self.cycles = cycles
	
	def __repr__(self):
		return self.username

class Leaderboards():
	def __init__(self, client, limit):
		self.limit = limit
		self.iterated = 0
		self.users = []
		self.raw_users = []
		self.next_cursor = None
		self.client = client
	
	def __await__(self):
		return self.load_all().__await__()
		
	def __aiter__(self):
		return self
	
	def __next__(self):
		raise NotImplementedError

	async def load_all(self):
		async for _ in self:
			pass
		return self.users

	async def __anext__(self):
		ended = len(self.users) + 1 > self.limit
		if self.iterated <= len(self.users) and not ended:
			self.iterated += 30
			leaderboard = await self.client._get_leaderboard(
				self.next_cursor
			)
			self.next_cursor = leaderboard['pageInfo']['nextCursor']
			self.raw_users.extend(leaderboard['items'])

		if ended:
			raise StopAsyncIteration
		u = self.raw_users[len(self.users)]
		user = User(
			self,
			u['id'],
			u['username'],
			u['image'],
			u['url'],
			u['karma']
		)
		
		self.users.append(user)
		return user
	
	def __repr__(self):
		if self.iterated >= self.limit:
			return f'<top {self.limit} leaderboard users (cached)>'
		return f'<top {self.limit} leaderboard users>'
	
	def __str__(self):
		return self.__repr__()


class graphql:
	'''
	All the graphql strings used
	'''
	create_comment = '''
mutation createComment($input: CreateCommentInput!) {
	createComment(input: $input) {
		comment {
			id
			...CommentDetailComment
			comments {
				id
				...CommentDetailComment
				__typename
			}
			parentComment {
				id
				__typename
			}
			__typename
		}
		__typename
	}
}

fragment CommentDetailComment on Comment {
	id
	body
	timeCreated
	canEdit
	canComment
	canReport
	hasReported
	url
	...CommentVoteControlComment
	user {
		id
		...UserPostHeaderUser
		__typename
	}
	post {
		id
		__typename
	}
	__typename
}

fragment UserPostHeaderUser on User {
	id
	username
	url
	image
	roles
	karma
	__typename
}

fragment CommentVoteControlComment on Comment {
	id
	voteCount
	canVote
	hasVoted
	__typename
}'''
	get_post = '''query post($id: Int!) {
	post(id: $id) {
		...EditPostPost
		__typename
	}
}

fragment EditPostPost on Post {
	id
	title
	body
	showHosted
	board {
		id
		replRequired
		__typename
	}
	repl {
		id
		url
		hostedUrl
		title
		__typename
	}
	__typename
}'''
	get_leaderboard = '''query leaderboard($after: String) {
	leaderboard(after: $after) {
		pageInfo {
			nextCursor
			__typename
		}
		items {
			id
			username
			image
			url
			karma
			__typename
		}
		__typename
	}
}'''
	get_all_posts = '''query posts($order: String, $after: String, $searchQuery: String) {
	posts(order: $order, after: $after, searchQuery: $searchQuery) {
		pageInfo {
			nextCursor
			__typename
		}
		items {
			id
			timeCreated
			...PostListItemPost
			board {
				id
				name
				url
				slug
				__typename
			}
			__typename
		}
		__typename
	}
}

fragment PostListItemPost on Post {
	id
	title
	body
	url
	commentCount
	isPinned
	isLocked
	isAnnouncement
	timeCreated
	...PostVoteControlPost
	user {
		id
		url
		username
		karma
		__typename
	}
	__typename
}

fragment PostVoteControlPost on Post {
	id
	voteCount
	canVote
	hasVoted
	__typename
}'''
	post_by_board='''query postsByBoard($id: Int!, $searchQuery: String, $postsOrder: String, $postsAfter: String) {
	postsByBoard(id: $id, searchQuery: $searchQuery, order: $postsOrder, after: $postsAfter) {
		pageInfo {
			nextCursor
			__typename
		}
		items {
			id
			...PostListItemPost
			__typename
		}
		__typename
	}
}

fragment PostListItemPost on Post {
	id
	title
	body
	url
	commentCount
	isPinned
	isLocked
	isAnnouncement
	timeCreated
	...PostVoteControlPost
	user {
		id
		url
		username
		karma
		__typename
	}
	__typename
}

fragment PostVoteControlPost on Post {
	id
	voteCount
	canVote
	hasVoted
	__typename
}'''
	get_comments = '''query post($id: Int!, $commentsOrder: String, $commentsAfter: String) {
	post(id: $id) {
		comments(order: $commentsOrder, after: $commentsAfter){
			pageInfo {
				nextCursor
				__typename
			}
			items {
				id
				...CommentDetailComment
				comments {
					id
					...CommentDetailComment
					__typename
				}
				__typename
			}
			__typename
		}
		__typename
	}
}

fragment UserPostHeaderUser on User {
	id
	username
	url
	image
	roles
	karma
	__typename
}

fragment CommentDetailComment on Comment {
	id
	body
	timeCreated
	canEdit
	canComment
	canReport
	hasReported
	url
	...CommentVoteControlComment
	user {
		id
		...UserPostHeaderUser
		__typename
	}
	post {
		id
		__typename
	}
	__typename
}

fragment CommentVoteControlComment on Comment {
	id
	voteCount
	canVote
	hasVoted
	__typename
}'''
	get_all_comments = '''
query comments($after: String) {
	comments(after: $after) {
		items {
			...CommentDetailComment
			comments {
				id
				...CommentDetailComment
				__typename
			}
		}
		pageInfo {
			hasNextPage
			nextCursor
		}
	}
}

fragment UserPostHeaderUser on User {
	id
	username
	url
	image
	roles
	karma
	__typename
}

fragment CommentDetailComment on Comment {
	id
	body
	timeCreated
	canEdit
	canComment
	canReport
	hasReported
	url
	...CommentVoteControlComment
	user {
		id
		...UserPostHeaderUser
		__typename
	}
	post {
		id
		__typename
	}
	__typename
}

fragment CommentVoteControlComment on Comment {
	id
	voteCount
	canVote
	hasVoted
	__typename
}

'''

class Client():
	def __init__(self):
		self.default_ref = base_url + '/@mat1/repl-talk-api'
		self.sid = None
		self.boards = self._boards(self)
	async def perform_graphql(self, operation_name, query, **variables):
		payload = {
			'operationName': operation_name,
			'variables': variables,
			'query': query
		}

		async with aiohttp.ClientSession(
			cookies={'connect.sid': self.sid},
			headers={'referer': self.default_ref}
		) as s:
			async with s.post(
				base_url + '/graphql',
				json=payload
			) as r:
				data = await r.json()
		if 'data' in data:
			data = data['data']
		keys = data.keys()
		if len(keys) == 1:
			data = data[next(iter(keys))]
		return data

	async def login(self, username, password):
		if username.lower() not in whitelisted_bots:
			raise NotWhitelisted(f'{username} is not whitelisted and therefore is not allowed to log in.\nPlease ask mat#6207 if you would like to be added to the whitelist.')

		# print('Logging in to Repl.it account')
		async with aiohttp.ClientSession(
			headers={'referer': self.refault_ref}
		) as s:
			async with s.post(
				base_url + '/login',
				json={
					'username': username,
					'password': password,
					'teacher': False
				}
			) as r:
				# Gets the connect.sid cookie
				connectsid = str(dict(r.cookies)['connect.sid'].value)
				# print('Gotten connect.sid')
				self.sid = connectsid
			return self

	async def _get_post(self, post_id):
		post = await self.perform_graphql(
			'post', graphql.get_post, id=post_id
		)
		return post

	async def get_post(self, post_id):
		post = await self._get_post(post_id)
		# print(post.keys())
		return Post(
			self,
			post['id'],
			post['title'],
			post['body'],
			post['showHosted'],
			post['board'],
			post['repl']
		)

	async def _get_leaderboard(self, cursor=None):
		if cursor is None:
			leaderboard = await self.perform_graphql(
				'leaderboard',
				graphql.get_leaderboard
			)
		else:
			leaderboard = await self.perform_graphql(
				'leaderboard',
				graphql.get_leaderboard,
				after=cursor
			)
		return leaderboard

	def get_leaderboard(self, limit=30):
		return Leaderboards(self, limit)

	async def _get_all_posts(
		self, order='new', search_query='', after=None
	):
		if after is None:
			posts = await self.perform_graphql(
				'posts',
				graphql.get_all_posts,
				order=order,
				searchQuery=search_query
			)
			return posts
		else:
			posts = await self.perform_graphql(
				'posts',
				graphql.get_all_posts,
				order=order,
				searchQuery=search_query,
				after=after
			)
			return posts

	async def _posts_in_board(
		self, order='new', search_query='', board_id=0, after=None
	):
		if board_id == 0:
			raise Exception('board id cant be 0')
		if after is None:
			posts = await self.perform_graphql(
				'postsByBoard',
				graphql.post_by_board,
				order=order,
				searchQuery=search_query,
				id=board_id
			)
			return posts
		else:
			posts = await self.perform_graphql(
				'postsByBoard',
				graphql.post_by_board,
				order=order,
				searchQuery=search_query,
				after=after,
				id=board_id
			)
			return posts
	
	class _boards:

		for board in ('all', 'announcements', 'challenge', 'ask', 'learn', 'share'):
			locals()['_' + board] = type(
				'_' + board,
				(Board,),
				{'name': board}
			)
			# Creates classes for each of the boards
		del board	# Don't want that extra class var


		def __init__(self, client):
			self.client = client
		
			self.all = self._all(client)
			self.announcements = self._announcements(client)
			self.challenge = self._challenge(client)
			self.ask = self._ask(client)
			self.learn = self._learn(client)
			self.share = self._share(client)

	async def _get_comments(self, post_id, order='new'):
		return await self.perform_graphql(
			'post',
			graphql.get_comments,
			id=post_id,
			commentsOrder=order
		)

	async def _get_user(self, username):
		raise NotImplementedError('This feature has yet to be added.')
	async def _get_all_comments(self):
		return await self.perform_graphql(
			'comments',
			graphql.get_all_comments,
			# after="23144"
		)
	async def get_all_comments(self):
		_comments = await self._get_all_comments()
		comments = []
		for c in _comments['items']:
			print(c.keys())
			comments.append(Comment(
				self,
				id=c['id'],
				body=c['body'],
				time_created=c['timeCreated'],
				can_edit=c['canEdit'],
				can_comment=c['canComment'],
				can_report=c['canReport'],
				has_reported=c['hasReported'],
				url=c['url'],
				votes=c['voteCount'],
				can_vote=c['canVote'],
				has_voted=c['hasVoted'],
				user=c['user'],
				post=c['post'],
				comments=c['comments']
			))
		return comments