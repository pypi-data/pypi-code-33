algorithm = """{algorithm(id: 1){state}}"""

algorithm_var = """query Algorithm($id:ID!){
  algorithm(id:$id){
    state
  }
}"""

algorithm_legacy = {
        "query": """{
            algorithm(id: 1){
                state
            }
        }
        """
    }

mutate_algorithm = """mutation UpdateAlgorithm($id:ID!, $state: String!){
    updateAlgorithm(id:$id, algorithm:{state: $state}){
        id
        state
    }
}"""

current_guid = '''
{
  optimizerRuns(
    orderBy: {
      desc: ID
    }
    limit: 1
  ){
    guid
    job{
      id
    }
  }
}
'''

current_guid_orders = '''
{
  orders (
    limit:1
    orderBy:{
      desc:ID
    }
    filter:{guid: "^[a-zA-Z0-9]"}
  ){
    guid
  }
}
'''

current_guid_government_inventories = '''
{
  governmentInventories (
    limit:1
    orderBy:{
      desc:ID
    }
    filter:{guid: "^[a-zA-Z0-9]"}
  ){
    guid
  }
}
'''

current_guid_black_books = '''
{
  blackBooks (
    limit:1
    orderBy:{
      desc:ID
    }
    filter:{guid: "^[a-zA-Z0-9]"}
  ){
    guid
  }
}
'''

create_notification = '''
mutation CreateNotification(
  $location: Location,
  $context: NotificationType,
  $title: String,
  $content: Text,
  $link: String,
  $linkText: String
){
  createNotification(
    location: $location
    read: false
    context: $context
    title: $title
    content: $content
    link: $link
    linkText: $linkText
  ){
    successful
    result{
      id
      context
    }
    messages{
      message
    }
  }
}
'''

create_order = """
mutation CreateOrder(
  $line_id: Int,
  $initial_date: String,
  $initial_hour: String,
  $final_date: String,
  $final_hour: String,
  $name: String,
  $description: String,
  $material_id: Int,
  $hectoliters: Int
){
  createOrder(
      lineId: $line_id, 
      initialDate: $initial_date, 
      initialHour: $initial_hour,
      finalDate: $final_date, 
      finalHour: $final_hour, 
      name: $name,
      description: $description,
      materialId: $material_id,
      hectoliters: $hectoliters
  ){
    successful
    result{
      id
    }
  }
}
"""

create_plan = """
mutation CreatePlan(
  	$guid: String,
    $line_id: Int,
    $order_id: Int,
    $start_at: NaiveDateTime,
  	$end_at: NaiveDateTime,
    $start_min: Int,
    $end_min: Int
)
{
    createPlan(
      			guid: $guid,
            lineId: $line_id,
            orderId: $order_id,
            startAt: $start_at,
            endAt: $end_at,
            startMin: $start_min,
            endMin: $end_min)
    {
      	successful
        result{
          id
        }
    }
}
"""

create_plan_historic = """
mutation CreatePlanHistoric(
    $plan: Text
)
{
    createPlanHistoric(
            plan: $plan
    )
    {
      	successful
        result{
          id
        }
    }
}
"""

create_plan_historic = """
mutation CreatePlanHistoric(
    $plan: Text
)
{
    createPlanHistoric(
            plan: $plan
    )
    {
      	successful
        result{
          id
        }
    }
}
"""

create_black_book_tank_plan = """
mutation CreateBlackBookTankPlan(
  $black_book_id: Int,
  $tank_plan_id: Int,
){
  createBlackBookTankPlan(
    blackBookId: $black_book_id,
    tankPlanId: $tank_plan_id
  ){
    successful
    result{
      id
    }
  }  
}
"""

create_tank_plan = """
mutation CreateTankPlan(
    $guid: String,
    $plan_id: Int,
    $line_end: NaiveDateTime ,
    $line_start: NaiveDateTime,
    $filter_id: Int,
    $filter_start: NaiveDateTime,
    $filter_end: NaiveDateTime,
    $filter_start_min: Int,
    $filter_end_min: Int,
    $water_quantity: Float,
    $lupulo: Float,
    $bisulfito: Float,
    $color: Float,
    $tank_id: Int,
    $government_tank_end: NaiveDateTime,
    $government_tank_start: NaiveDateTime,
    $government_tank_end_min: Int,
    $government_tank_start_min: Int,
    $hectoliter: Int,
    $order_id: Int,
    $percentage: Int,
)
{
    createTankPlan(
        guid: $guid,
        planId: $plan_id,
        lineEnd: $line_end,
        lineStart: $line_start,
        filterId: $filter_id,
        filterStart: $filter_start,
        filterEnd: $filter_end,
        filterStartMin: $filter_start_min,
        filterEndMin: $filter_end_min,
        waterQuantity: $water_quantity,
        lupulo: $lupulo,
        bisulfito: $bisulfito,
        color: $color,
        tankId: $tank_id,
        governmentTankEnd: $government_tank_end,
        governmentTankStart: $government_tank_start,
        governmentTankEndMin: $government_tank_end_min,
        governmentTankStartMin: $government_tank_start_min,
        hectoliter: $hectoliter,
        orderId: $order_id,
        percentage: $percentage,
        ){
          result{
            id
          }
          messages{
            message
            field
          }
        }
}
"""

create_tank_plan_no_filters = """
mutation CreateTankPlan(
    $guid: String,
    $plan_id: Int,
    $line_end: NaiveDateTime ,
    $line_start: NaiveDateTime,
    $tank_id: Int,
    $government_tank_end: NaiveDateTime,
    $government_tank_start: NaiveDateTime,
    $government_tank_end_min: Int,
    $government_tank_start_min: Int,
    $hectoliter: Int,
    $order_id: Int,
    $percentage: Int
)
{
    createTankPlan(
        guid: $guid,
        planId: $plan_id,
        lineEnd: $line_end,
        lineStart: $line_start,
        tankId: $tank_id,
        governmentTankEnd: $government_tank_end,
        governmentTankStart: $government_tank_start,
        governmentTankEndMin: $government_tank_end_min,
        governmentTankStartMin: $government_tank_start_min,
        hectoliter: $hectoliter,
        orderId: $order_id,
        percentage: $percentage,
        ){
          result{
            id
          }
        }
}
"""

all_aliases = '''{
  materials{
  name
  alias
  }
}'''

all_brands = """
{
  materials(
    filter:{
      codeMaterial:"MARCA"
    }){
    id
    name
    materialType
    colorStandard
    lupuloStandard
    bisulfitoStandard
    wortId
    wort{
        name
        minimumRestDays
    }
    concentrationType
  }
}
"""

all_worts = '''
{
  worts{
    name
    materials{
      name
      concentrationType
      concentrationValue
  		colorRequired
      colorStandard
      lupuloRequired
      lupuloStandard
      pvppRequired
      pvppStandard
      bisulfitoRequired
      bisulfitoStandard
      bicarbonatoRequired
      bicarbonatoStandard
    }
    minimumRestDays
  }
}
'''

all_consumers='''{
  materials{
  name
    materialConsumers{
      consumer{
        name
      }
    }
  }
}'''

all_filters = """
{
    filters{
        id
        name
      	description
      	alias
        nominalSpeed
    }
}
"""

all_lines = """
{
  lines{
    id
    name
    room{
      name
    }
  }
}
"""

all_orders_guid = """
{
    orders
    (
      filter: {
        guid: "%s"
      }
    )
    {
        id
        line{
            name
        },
        initialDate,
        initialHour,
        finalDate,
        finalHour,
        name,
        description,
        material{
            name
        },
        hectoliters,
        finished
    }
}
""" 

all_orders = """
{
    orders
    {
        id
        line{
            name
        },
        initialDate,
        initialHour,
        finalDate,
        finalHour,
        name,
        description,
        material{
            name
        },
        hectoliters,
        finished
    }
}
""" 
all_government_tank_status_catalogue= """
{
 govTankStatusCatalogues{
  status
   description
   alias
 }
}
"""

all_government_inventories_guid = """{tanks(
  filter:{
    name:"^L"
  }
  orderBy:{
    asc:INSERTED_AT
  }
){
  name
  capacity
  room{
    name
  }
  governmentInventories(
    orderBy:{
      desc: INSERTED_AT
    }
    filter: {
      guid: "%s"
    }
    limit: 1
  ){
    insertedAt
    material{
      name
    }
    hectoliters
    status
    }
  }
}
"""

all_government_inventories = """
{tanks(
  filter:{
    tankType:"GOBIERNO"
  }
  orderBy:{
    asc:INSERTED_AT
  }
){
  name
  capacity
  room{
    name
  }
  governmentInventories(
    orderBy:{
      desc: INSERTED_AT
    }
    limit: 1
  ){
    insertedAt
    material{
      name
    }
    hectoliters
    status
    }
  }
}
"""

all_tanks = """
{
  tanks{
    id
    name
    room{
      name
    }
    capacity
  }
}
"""

all_tank_plans = """
{
  tankPlans{
    id
    filterId
    planId
    orderId
    filterStart
    filterEnd
    hectoliter
  }
}
"""

all_plans = """
{
  plans{
    id
    order{
      hectoliters
    }
    startAt
    endAt
  }
}
"""

all_black_books_guid = """
query BlackBooks {
  tanks (
    filter: {
      name: "^R"
    }
    orderBy: {
      asc: NAME
    }
  ) {
    id
    name
    blackBooks(
      filter: {guid: "%s"}
      orderBy: {desc: ID}
      limit: 1
    ) {
      guid
      wort{
        id
        name
      }
      fillingRestTankDate
      hectoliters
      originalExtract
      bitterBu
      colorEbc
      so2Total
      alcoholPercentage
    }
  }
}
"""

all_black_books = """
{tanks(
  filter:{
    tankType:"REPOSO"
  }
  orderBy:{
    asc:INSERTED_AT
  }
){
  name,
  blackBooks(
    orderBy:{
      desc: INSERTED_AT
    }
    limit: 1
  )
  {
    id
    tankId
    fillingRestTankDate
    wort{
      name
      minimumRestDays
    },
    alcoholPercentage,
    originalExtract,
    hectoliters,
    bitterBu,
    colorEbc,
    so2Total
    }
  }
}
"""

marcas='''{
    materials(filter:{codeMaterial:"MARCA"}){
        name
        codeMaterial
        lupuloStandard
        }
    }'''

mostos='''{
    materials(filter:{codeMaterial:"MOSTO"}){
        name
        minimumRestDays
        codeMaterial
    }
    }'''

all_jobs='''{
    jobs(
        orderBy:{
            asc:ID
        }
        filter:{
            status:WAITING
        }
    ){
        id
        function
        input
        status
    }
    }'''

update_job='''
mutation UpdateJob(
    $id:ID!
    $status:JobStatus!
    $output:Text!
    ){
    updateJob(
        id:$id
        job:{
        status:$status
        output:$output
        }
    ){
        successful
        messages{
        message
        }
    }
}
'''

update_tank_plan_filter = '''
mutation updateTankPlanFilter(
  $id: ID!,
  $filterProgress: Float,
  $lineProgress: Float
){
  updateTankPlan(
    id: $id, 
    tankPlan: {
      filterProgress: $filterProgress,
      lineProgress: $lineProgress
    }
  ){
    successful
  }
}
'''

update_plan_progress = '''
mutation updatePlanProgress(
  $id: ID!,
  $progress: Float
){
  updatePlan(
    id: $id, 
    plan: {
      progress: $progress
    }
  ){
    successful
  }
}
'''

last_change_sap = '''
{
  auditLogs(
    limit:1
    orderBy: {desc: ID}
    filter:{
      resource:"^%s$"
      actorId:"12"
    }
  ){
    id
    actorId
    resource
    resourceId
    insertedAt
  }
}
'''

optimizer_run='''
{
  optimizerRuns(orderBy: {desc: ID} #filter: {id: 251}
   limit : 1){
    id
    version
    guid
    ordersGuid
    blackbooksGuid
    governmentInventoryGuid
    updatedAt
    job{
      id
      status
      input
      progress
    }
  }
}
'''

update_optimizer_run = '''
mutation updateOptimizerRun(
  $id: Int,
  $plan_historic_id: Int,
  $guid: String,
  $orders_guid:String,
  $government_inventory_guid:String,
  $black_books_guid: String
){
  updateOptimizerRun(
    id: $id,
    optimizerRun:{
    planHistoricId: $plan_historic_id,
      guid: $guid,
      ordersGuid:$orders_guid,
      governmentInventoryGuid: $government_inventory_guid,
      blackbooksGuid: $black_books_guid  
    }
  ){
    successful
    result{
      id
    }
  }
}
'''

sap_not_working_alert = '''
mutation {
  createNotification(
    title: "Falla de conexión con SAP"
    location: ALERT
    context: DANGER
    content: "%s sin conexión desde hace %d min"
    read: false
  ){
    successful
    messages{
      message
    }
  }
}
'''

create_optimizer_run='''
mutation CreateOptimizationRun(
  $planHistoricId: Int,
  $guid: String,
  $ordersGuid: String,
  $governmentInventoryGuid: String,
  $blackbooksGuid: String
){
  createOptimizerRun(
      planHistoricId: $planHistoricId,
      guid: $guid,
      ordersGuid:$ordersGuid,
      governmentInventoryGuid: $governmentInventoryGuid,
        blackbooksGuid:$blackbooksGuid
){
  successful
  result{
    id
  }
}
}
'''
sap_not_working_activity = '''
mutation {
  createNotification(
    location: ACTIVITY
	title: "Falla de conexión con SAP"
    content: "%s sin conexión desde hace %d min"
    read: false
  ){
    successful
    messages{
      message
    }
  }
}
'''

order = '''
{
  order(
    id: %s
  )
  {
    hectoliters
  }
}
'''