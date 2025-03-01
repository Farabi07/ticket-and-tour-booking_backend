from django.db import migrations


class Migration(migrations.Migration):
    

    dependencies = [
        ('loginmodule', '0002_login_avatar'),
    ]

    def insertData(apps, schema_editor):
        PrimaryGroup = apps.get_model('account', 'PrimaryGroup')
        Group = apps.get_model('account', 'Group')
        LedgerAccount = apps.get_model('account', 'LedgerAccount')
        
        # primary groups
        pg_assets = PrimaryGroup.objects.create(name="Assets", is_deletable=False)
        pg_liabilities = PrimaryGroup.objects.create(name="Liabilities",)
        pg_expenses = PrimaryGroup.objects.create(name="Expenses", is_deletable=False)
        pg_income = PrimaryGroup.objects.create(name="Incomes", is_deletable=False)



        # groups under pg_assets
        g_current_assets = Group.objects.create(name='Current Assets', head_primarygroup=pg_assets, is_deletable=False)
        g_fixed_assets = Group.objects.create(name='Fixed Assets', head_primarygroup=pg_assets, is_deletable=False)
        g_investments = Group.objects.create(name='Investments', head_primarygroup=pg_assets, is_deletable=False)
        g_misc_expenses = Group.objects.create(name='Misc. Expenses (ASSETS)', head_primarygroup=pg_assets, is_deletable=False)

        # groups under g_current_assets
        g_bank_accounts = Group.objects.create(name='Bank Accounts', head_group=g_current_assets, is_deletable=False)
        g_cash_in_hand = Group.objects.create(name='Cash-in-Hand', head_group=g_current_assets, is_deletable=False)
        g_deposits = Group.objects.create(name='Deposits (Asssets)', head_group=g_current_assets, is_deletable=False)
        g_loans_and_advances = Group.objects.create(name='Loans And Advances (Assets)', head_group=g_current_assets, is_deletable=False)
        g_stock_in_hand = Group.objects.create(name='Stock-in-Hand', head_group=g_current_assets, is_deletable=False)
        g_sundry_debtors = Group.objects.create(name='Sundry Debtors', head_group=g_current_assets, is_deletable=False)

        # group under g_sundry_debtors
        g_customer = Group.objects.create(name='Customers', head_group=g_sundry_debtors, is_deletable=False)

        # ledger under g_bank_accounts
        l_bank = LedgerAccount.objects.create(name='Bank', head_group=g_bank_accounts, is_deletable=False)

        # ledger under g_cash_in_hand
        l_cash = LedgerAccount.objects.create(name='Cash', head_group=g_cash_in_hand, is_deletable=False)

        # ledger under g_customer
        l_opening_balance_of_customer = LedgerAccount.objects.create(name='Opening Balance Of Customer', head_group=g_customer, is_deletable=False)



        # groups under pg_liabilities
        g_branch_or_divisions = Group.objects.create(name='Branch / Divisions', head_primarygroup=pg_liabilities, is_deletable=False)
        g_capital_account = Group.objects.create(name='Capital Account', head_primarygroup=pg_liabilities, is_deletable=False)
        g_current_liabilities = Group.objects.create(name='Current Liabilities', head_primarygroup=pg_liabilities, is_deletable=False)
        g_salary = Group.objects.create(name='Salary', head_primarygroup=pg_liabilities, is_deletable=False)
        g_investment = Group.objects.create(name='Investment', head_primarygroup=pg_liabilities, is_deletable=False)
        g_loans = Group.objects.create(name='Loans (Liability)', head_primarygroup=pg_liabilities, is_deletable=False)
        g_suspense_acc = Group.objects.create(name='Suspense A/C', head_primarygroup=pg_liabilities, is_deletable=False)
        l_profit_and_loss = LedgerAccount.objects.create(name='Profit & Loss A/C', head_primarygroup=pg_liabilities, is_deletable=False)

        # groups under g_capital_account
        g_reserves_and_surplus = Group.objects.create(name='Reserves & Surplus', head_group=g_capital_account, is_deletable=False)

        # groups under g_current_liabilities
        g_duties_and_taxes = Group.objects.create(name='Duties & Taxes', head_group=g_current_liabilities, is_deletable=False)
        g_provisions = Group.objects.create(name='Provisions', head_group=g_current_liabilities, is_deletable=False)
        g_sundry_creditors = Group.objects.create(name='Sundry Creditors', head_group=g_current_liabilities, is_deletable=False)

        # groups under g_sundry_creditors
        g_suppliers = Group.objects.create(name='Suppliers', head_group=g_sundry_creditors, is_deletable=False)

        # groups under g_loans
        g_bank_od_acc = Group.objects.create(name='Bank OD A/C', head_group=g_loans, is_deletable=False)
        g_secured_loans = Group.objects.create(name='Secured Loans', head_group=g_loans, is_deletable=False)
        g_unsecured_loans = Group.objects.create(name='Unsecured Loans', head_group=g_loans, is_deletable=False)



        # groups under pg_expenses
        g_direct_expenses = Group.objects.create(name='Direct Expenses', head_primarygroup=pg_expenses, is_deletable=False)
        g_indirect_expenses = Group.objects.create(name='Indirect Expenses', head_primarygroup=pg_expenses, is_deletable=False)
        g_purchase_accounts = Group.objects.create(name='Purchase Accounts', head_primarygroup=pg_expenses, is_deletable=False)

        # ledger under g_purchase_accounts
        l_company_purchase = LedgerAccount.objects.create(name='Company Purchase', head_group=g_purchase_accounts, ledger_type='Company Purchase', is_deletable=False)



        # groups under pg_income
        g_direct_incomes = Group.objects.create(name='Direct Incomes', head_primarygroup=pg_income, is_deletable=False)
        g_indirect_incomes = Group.objects.create(name='Indirect Incomes', head_primarygroup=pg_income, is_deletable=False)
        g_sales_accounts = Group.objects.create(name='Sales Accounts', head_primarygroup=pg_income, is_deletable=False)

        # ledger under g_sales_accounts
        l_company_sales = LedgerAccount.objects.create(name='Company Sales', head_group=g_sales_accounts, ledger_type='Company Sales', is_deletable=False)



    operations = [
        migrations.RunPython(insertData),
    ]
