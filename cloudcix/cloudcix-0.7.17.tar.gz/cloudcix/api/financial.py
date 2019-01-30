from cloudcix.client import Client


class Financial:
    """
    The Financial Application exposes a suite of services that together implement a full accounting system based on
    double entry bookkeeping
    """
    _application_name = 'Financial'

    account_purchase_adjustment = Client(
        _application_name,
        'AccountPurchaseAdjustment/',
    )
    account_purchase_adjustment_contra = Client(
        _application_name,
        'AccountPurchaseAdjustment/{address_id}/Contra/',
    )
    account_purchase_debit_note = Client(
        _application_name,
        'AccountPurchaseDebitNote/',
    )
    account_purchase_debit_note_contra = Client(
        _application_name,
        'AccountPurchaseDebitNote/{address_id}/Contra/',
    )
    account_purchase_invoice = Client(
        _application_name,
        'AccountPurchaseInvoice/',
    )
    account_purchase_invoice_contra = Client(
        _application_name,
        'AccountPurchaseInvoice/{address_id}/Contra/',
    )
    account_purchase_payment = Client(
        _application_name,
        'AccountPurchasePayment/',
    )
    account_purchase_payment_contra = Client(
        _application_name,
        'AccountPurchasePayment/{address_id}/Contra/',
    )
    account_sale_adjustment = Client(
        _application_name,
        'AccountSaleAdjustment/',
    )
    account_sale_adjustment_contra = Client(
        _application_name,
        'AccountSaleAdjustment/{address_id}/Contra/',
    )
    account_sale_credit_note = Client(
        _application_name,
        'AccountSaleCreditNote/',
    )
    account_sale_credit_note_contra = Client(
        _application_name,
        'AccountSaleCreditNote/{address_id}/Contra/',
    )
    account_sale_invoice = Client(
        _application_name,
        'AccountSaleInvoice/',
    )
    account_sale_invoice_contra = Client(
        _application_name,
        'AccountSaleInvoice/{address_id}/Contra/',
    )
    account_sale_payment = Client(
        _application_name,
        'AccountSalePayment/',
    )
    account_sale_payment_contra = Client(
        _application_name,
        'AccountSalePayment/{address_id}/Contra/',
    )
    allocation = Client(
        _application_name,
        'Allocation/',
    )
    business_logic = Client(
        _application_name,
        'BusinessLogic/',
    )
    cash_purchase_debit_note = Client(
        _application_name,
        'CashPurchaseDebitNote/',
    )
    cash_purchase_debit_note_contra = Client(
        _application_name,
        'CashPurchaseDebitNote/{address_id}/Contra/',
    )
    cash_purchase_invoice = Client(
        _application_name,
        'CashPurchaseInvoice/',
    )
    cash_purchase_invoice_contra = Client(
        _application_name,
        'CashPurchaseInvoice/{address_id}/Contra/',
    )
    cash_sale_credit_note = Client(
        _application_name,
        'CashSaleCreditNote/',
    )
    cash_sale_credit_note_contra = Client(
        _application_name,
        'CashSaleCreditNote/{address_id}/Contra/',
    )
    cash_sale_invoice = Client(
        _application_name,
        'CashSaleInvoice/',
    )
    cash_sale_invoice_contra = Client(
        _application_name,
        'CashSaleInvoice/{address_id}/Contra/',
    )
    creditor_account_history = Client(
        _application_name,
        'CreditorAccount/{id}/History/',
    )
    creditor_account_statement = Client(
        _application_name,
        'CreditorAccount/{id}/Statement/',
    )
    creditor_account_statement_log = Client(
        _application_name,
        'CreditorAccount/{id}/Statement/',
    )
    creditor_ledger = Client(
        _application_name,
        'CreditorLedger/',
    )
    creditor_ledger_aged = Client(
        _application_name,
        'CreditorLedger/Aged/',
    )
    creditor_ledger_transaction = Client(
        _application_name,
        'CreditorLedger/Transaction/',
    )
    creditor_ledger_transaction_contra = Client(
        _application_name,
        'CreditorLedger/ContraTransaction/',
    )
    debtor_account_history = Client(
        _application_name,
        'DebtorAccount/{id}/History/',
    )
    debtor_account_statement = Client(
        _application_name,
        'DebtorAccount/{id}/Statement/',
    )
    debtor_account_statement_log = Client(
        _application_name,
        'DebtorAccount/StatementLog/',
    )
    debtor_ledger = Client(
        _application_name,
        'DebtorLedger/',
    )
    debtor_ledger_aged = Client(
        _application_name,
        'DebtorLedger/Aged/',
    )
    debtor_ledger_transaction = Client(
        _application_name,
        'DebtorLedger/Transaction/',
    )
    debtor_ledger_transaction_contra = Client(
        _application_name,
        'DebtorLedger/ContraTransaction/',
    )
    journal_entry = Client(
        _application_name,
        'JournalEntry/',
    )
    nominal_account = Client(
        _application_name,
        'NominalAccount/',
    )
    nominal_account_history = Client(
        _application_name,
        'NominalAccount/{id}/History/',
    )
    nominal_account_type = Client(
        _application_name,
        'NominalAccountType/',
    )
    nominal_contra = Client(
        _application_name,
        'NominalContra/',
    )
    nominal_ledger_balance_sheet = Client(
        _application_name,
        'NominalLedger/BalanceSheet/',
    )
    nominal_ledger_profit_loss = Client(
        _application_name,
        'NominalLedger/ProfitLoss/',
    )
    nominal_ledger_purchases_by_country = Client(
        _application_name,
        'NominalLedger/PurchasesByCountry/',
    )
    nominal_ledger_sales_by_country = Client(
        _application_name,
        'NominalLedger/SalesByCountry/',
    )
    nominal_ledger_trial_balance = Client(
        _application_name,
        'NominalLedger/TrialBalance/',
    )
    nominal_ledger_vies_purchases = Client(
        _application_name,
        'NominalLedger/VIESPurchases/',
    )
    nominal_ledger_vies_sales = Client(
        _application_name,
        'NominalLedger/VIESSales/',
    )
    payment_method = Client(
        _application_name,
        'PaymentMethod/',
    )
    period_end = Client(
        _application_name,
        'PeriodEnd/',
    )
    tax_rate = Client(
        _application_name,
        'TaxRate/',
    )
    year_end = Client(
        _application_name,
        'YearEnd/',
    )
