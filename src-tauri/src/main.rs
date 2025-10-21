#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use anyhow::Result;
use dotenv::dotenv;

mod config;
mod database;
mod handlers;
mod models;
mod services;

use services::{BundleService, ItemService, ProgressService};

pub struct AppState {
    pub item_service: ItemService,
    pub bundle_service: BundleService,
    pub progress_service: ProgressService,
}

#[tokio::main]
async fn main() -> Result<()> {
    dotenv().ok();

    println!("Starting Junimo...");

    // Initialize database connection
    let db = database::init().await?;
    println!("Database connection established");

    // Run migrations
    database::migrate(&db).await?;
    println!("Database migrations completed");

    // Test database connection by counting items
    let item_count: (i64,) = sqlx::query_as("SELECT COUNT(*) FROM items")
        .fetch_one(&db)
        .await?;
    println!("Found {} items in database", item_count.0);

    // Initialize services
    let app_state = AppState {
        item_service: ItemService::new(db.clone()),
        bundle_service: BundleService::new(db.clone()),
        progress_service: ProgressService::new(db.clone()),
    };

    println!("Services initialized");

    println!("Starting Tauri application...");

    tauri::Builder::default()
        .manage(app_state)
        .invoke_handler(tauri::generate_handler![
            handlers::get_items,
            handlers::search_items,
            handlers::get_bundles,
            handlers::get_bundle_items,
            handlers::mark_item_completed,
            handlers::mark_item_incomplete,
            handlers::get_progress
        ])
        .setup(|app| {
            println!("Tauri setup complete, window should be opening...");
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");

    println!("Tauri application finished");

    println!("Junimo started successfully!");
    Ok(())
}
