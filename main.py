import json
import argparse
from typing import Dict, Any
from decorators.registry import get_seeder, get_faker
from dotenv import load_dotenv

from seeders import *
from fakers import *

def load_seed_config(config_path: str = "config/seed_config.json") -> Dict[str, Any]:
    try:
        with open(config_path) as f:
            return json.load(f)
    except FileNotFoundError:
        return {"default_counts": {}}
    except json.JSONDecodeError:
        return {"default_counts": {}}

def parse_arguments():
    parser = argparse.ArgumentParser(description="Database Seeder Tool")
    
    parser.add_argument(
        "-c", "--config",
        default="config/seed_config.json",
        help="Path to seed configuration JSON file"
    )
    parser.add_argument(
        "--users", type=int,
        help="Number of users to seed (overrides config)"
    )
    parser.add_argument(
        "--roles", type=int,
        help="Number of roles to seed (overrides config)"
    )
    parser.add_argument(
        "--permissions", type=int,
        help="Number of permissions to seed (overrides config)"
    )
    parser.add_argument(
        "--features", type=int,
        help="Number of features to seed (overrides config)"
    )
    parser.add_argument(
        "--role-permissions", type=int,
        help="Number of role-permission relations to seed (overrides config)"
    )
    parser.add_argument(
        "--user-roles", type=int,
        help="Number of user-role relations to seed (overrides config)"
    )
    parser.add_argument(
        "--service-providers", type=int,
        help="Number of service providers to seed (overrides config)"
    )
    parser.add_argument(
        "--travel-tickets", type=int,
        help="Number of travel tickets to seed (overrides config)"
    )
    parser.add_argument(
        "--payment-methods", type=int,
        help="Number of payment methods to seed (overrides config)"
    )
    parser.add_argument(
        "--user-reservations", type=int,
        help="Number of user reservations to seed (overrides config)"
    )
    parser.add_argument(
        "--payments", type=int,
        help="Number of payments to seed (overrides config)"
    )
    parser.add_argument(
        "--reports", type=int,
        help="Number of reports to seed (overrides config)"
    )
    parser.add_argument(
        "--notifications", type=int,
        help="Number of notifications to seed (overrides config)"
    )
    parser.add_argument(
        "--refund-requests", type=int,
        help="Number of refund requests to seed (overrides config)"
    )
    parser.add_argument(
        "--reviews", type=int,
        help="Number of reviews to seed (overrides config)"
    )
    parser.add_argument(
        "--train-details", type=int,
        help="Number of train details to seed (overrides config)"
    )
    parser.add_argument(
        "--flight-details", type=int,
        help="Number of flight details to seed (overrides config)"
    )
    parser.add_argument(
        "--bus-details", type=int,
        help="Number of bus details to seed (overrides config)"
    )
    parser.add_argument(
        "--bus-features", type=int,
        help="Number of bus features to seed (overrides config)"
    )
    parser.add_argument(
        "--train-features", type=int,
        help="Number of train features to seed (overrides config)"
    )
    parser.add_argument(
        "--flight-features", type=int,
        help="Number of flight features to seed (overrides config)"
    )
    parser.add_argument(
        "--discounts", type=int,
        help="Number of discounts to seed (overrides config)"
    )
    parser.add_argument(
        "--user-loyalties", type=int,
        help="Number of user loyalties to seed (overrides config)"
    )
    parser.add_argument(
        "--user-discounts", type=int,
        help="Number of user discounts to seed (overrides config)"
    )
    parser.add_argument(
        "--ticket-discounts", type=int,
        help="Number of ticket discounts to seed (overrides config)"
    )
    parser.add_argument(
        "--user-referrals", type=int,
        help="Number of user referrals to seed (overrides config)"
    )
    parser.add_argument(
        "--support-categories", type=int,
        help="Number of support categories to seed (overrides config)"
    )
    parser.add_argument(
        "--support-tickets", type=int,
        help="Number of support tickets to seed (overrides config)"
    )
    parser.add_argument(
        "--support-conversations", type=int,
        help="Number of support conversations to seed (overrides config)"
    )
    parser.add_argument(
        "--ticket-cancellations", type=int,
        help="Number of ticket cancellations to seed (overrides config)"
    )
    parser.add_argument(
        "-n", "--count", type=int,
        help="Default count for all tables (overrides config)"
    )
    parser.add_argument(
        "-l", "--list",
        action="store_true",
        help="List all available tables and exit"
    )
    
    return parser.parse_args()

def get_seed_counts(args, config: Dict[str, Any]) -> Dict[str, int]:
    counts = config.get("default_counts", {}).copy()
    
    if args.count:
        counts = {table: args.count for table in counts}
    
    table_args = {
        "users": args.users,
        "roles": args.roles,
        "permissions": args.permissions,
        "features": args.features,
        "role_permissions": args.role_permissions,
        "user_roles": args.user_roles,
        "service_providers": args.service_providers,
        "travel_tickets": args.travel_tickets,
        "payment_methods": args.payment_methods,
        "user_reservations": args.user_reservations,
        "payments": args.payments,
        "reports": args.reports,
        "notifications": args.notifications,
        "refund_requests": args.refund_requests,
        "reviews": args.reviews,
        "train_details": args.train_details,
        "flight_details": args.flight_details,
        "bus_details": args.bus_details,
        "bus_features": args.bus_features,
        "train_features": args.train_features,
        "flight_features": args.flight_features,
        "discounts": args.discounts,
        "user_loyalties": args.user_loyalties,
        "user_discounts": args.user_discounts,
        "ticket_discounts": args.ticket_discounts,
        "user_referrals": args.user_referrals,
        "support_categories": args.support_categories,
        "support_tickets": args.support_tickets,
        "support_conversations": args.support_conversations,
        "ticket_cancellations": args.ticket_cancellations
    }
    
    for table_name, arg_value in table_args.items():
        if arg_value is not None:
            counts[table_name] = arg_value
    
    return counts

def list_tables():
    print("Available Seeders:")
    for table, info in get_seeder().items():
        print(f"- {table.ljust(20)} (Dependencies: {', '.join(info['dependencies']) or 'None'})")
    
    print("\nAvailable Fakers:")
    for table, func in get_faker().items():
        print(f"- {table}")

def main():
    load_dotenv()
    args = parse_arguments()
    config = load_seed_config(args.config)

    if args.list:
        list_tables()
        return

    counts = get_seed_counts(args, config)

    user_specified_tables = {
        table: count for table, count in counts.items()
        if getattr(args, table.replace('-', '_'), None) is not None
    }

    manager = SeederManager()

    if user_specified_tables:
        print("Seeding selected tables:")
        results = {}
        for table_name, count in user_specified_tables.items():
            try:
                result = manager.seed_table(table_name, count)
                results[table_name] = result
                print(f"{table_name.ljust(25)}: {result} records")
            except Exception as e:
                print(f"Error seeding {table_name}: {e}")
    else:
        print("Seeding all tables from config or default counts...")
        results = manager.seed_all(counts)
        print("\nSeeding Summary:")
        for table, count in results.items():
            print(f"{table.ljust(25)}: {count} records")

if __name__ == "__main__":
    main()