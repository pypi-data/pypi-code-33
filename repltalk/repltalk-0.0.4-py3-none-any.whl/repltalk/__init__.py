import aiohttp

# bots approved by the replit team that are allowed to log in
whitelisted_bots = {
	'repltalk'
}

base_url = 'https://repl.it'

class NotWhitelisted(Exception):pass

class Post():
	def __init__(
		self, client, id, title, body, show_hosted, board, repl
	):
		self.client = client
		self.id = id
		self.title = title
		self.body = body
		self.show_hosted = show_hosted
		self.board = board
		self.repl = repl
	async def get_comments(self):
		return 'todo'

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
	def __str__(self):
		return self.username
	def __repr__(self):
		return self.username

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

class Client():
	def __init__(self):
		self.default_ref = base_url + '/@mat1/repl-talk-api'
		self.sid = None

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
		print(post.keys())
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

	async def get_leaderboard(self, limit=30):
		next_cursor = None
		all_users = []
		while limit > 0:
			leaderboard = await self._get_leaderboard(
				next_cursor
			)
			next_cursor = leaderboard['pageInfo']['nextCursor']
			all_users.extend(leaderboard['items'])
			limit -= 30
		users = tuple(
			User(
				self,
				u['id'],
				u['username'],
				u['image'],
				u['url'],
				u['karma']
			) for u in all_users
		)
		return users