import aiohttp

# bots approved by the replit team that are allowed to log in
whitelisted_bots = {
	'repltalk'
}

base_url = 'https://repl.it' # Why not the repl talk base url?

class NotWhitelisted(Exception):pass

board_ids = {
	'share': 3,
	'ask': 6,
	'announcements': 14,
	'challenge': 16,
	'learn': 17
}

class board():
	@classmethod
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
				raise NotImplemented('TODO: create a proper error here')
		# print(self, '_get_posts called.') 
	
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
		# TODO: convert posts to list of Post objects
		# Never will happen
		return posts
Board = board # Alias for board class matching PEP8


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
	
	async def get_comments(self):
		return 'todo'
	
	def __repr__(self):
		return f'<{self.title}>'
	
	def __eq__(self, post2):
		return self.id == post2.id
	
	def __ne__(self, post2):
		return self.id != post2.id

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
		return NotImplemented

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
		def __init__(self, client):
			self.client = client
		
			self.all = self._all(client)
			self.announcements = self._announcements(client)
			self.challenge = self._challenge(client)
			self.ask = self._ask(client)
			self.learn = self._learn(client)
			self.share = self._share(client)
		class _all(board):
			def __init__(self, client):
				self.client = client
				self.name = 'all'
		class _announcements(board):
			def __init__(self, client):
				self.client = client
				self.name = 'announcements'
		class _challenge(board):
			def __init__(self, client):
				self.client = client
				self.name = 'challenge'
		class _ask(board):
			def __init__(self, client):
				self.client = client
				self.name = 'ask'
		class _learn(board):
			def __init__(self, client):
				self.client = client		
				self.name = 'learn'
		class _share(board):
			def __init__(self, client):
				self.client = client
				self.name = 'share'