# Nash Core Margin Manager Specifications
## User Expectations
 - Add orders using the margin manager
 - When filling order, update properly:
     - Add the benefit from price improvement (INC PORTION) to the avblBalance
     - Change the reduciblePosition for the assosciated MarginManager object
     - Call allocReducible in the MarginManager
 - When removing order, change redOrders, incOrders and avblPosition accordingly, then call allocReducible
