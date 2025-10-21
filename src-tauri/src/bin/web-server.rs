use anyhow::Result;
use dotenv::dotenv;
use poem::{
    get, handler,
    listener::TcpListener,
    middleware::Cors,
    post,
    web::{Data, Json, Path, Query},
    EndpointExt, Route, Server,
};
use serde::{Deserialize, Serialize};

use tokio;

// Import the existing modules
use junimo::database;
use junimo::models::{Bundle, BundleItem, Item, UserProgress};
use junimo::services::{BundleService, ItemService, ProgressService};

// Shared application state
#[derive(Clone)]
pub struct AppState {
    pub item_service: ItemService,
    pub bundle_service: BundleService,
    pub progress_service: ProgressService,
}

// Request/Response types
#[derive(Deserialize)]
struct SearchQuery {
    q: Option<String>,
}

#[derive(Deserialize)]
struct ProgressRequest {
    #[serde(rename = "bundleItemId")]
    bundle_item_id: i32,
}

#[derive(Serialize)]
struct ApiResponse<T> {
    success: bool,
    data: Option<T>,
    error: Option<String>,
}

impl<T> ApiResponse<T> {
    fn success(data: T) -> Self {
        Self {
            success: true,
            data: Some(data),
            error: None,
        }
    }

    fn error(message: String) -> Self {
        Self {
            success: false,
            data: None,
            error: Some(message),
        }
    }
}

// API Handlers
#[handler]
async fn get_items(Data(state): Data<&AppState>) -> poem::Result<Json<ApiResponse<Vec<Item>>>> {
    println!("GET /api/items");
    match state.item_service.get_all_items().await {
        Ok(items) => {
            println!("Successfully retrieved {} items", items.len());
            Ok(Json(ApiResponse::success(items)))
        }
        Err(e) => {
            println!("Error retrieving items: {}", e);
            Ok(Json(ApiResponse::error(e.to_string())))
        }
    }
}

#[handler]
async fn search_items(
    Query(query): Query<SearchQuery>,
    Data(state): Data<&AppState>,
) -> poem::Result<Json<ApiResponse<Vec<Item>>>> {
    let search_term = query.q.unwrap_or_default();
    println!("GET /api/items/search?q={}", search_term);

    if search_term.is_empty() {
        match state.item_service.get_all_items().await {
            Ok(items) => return Ok(Json(ApiResponse::success(items))),
            Err(e) => return Ok(Json(ApiResponse::error(e.to_string()))),
        }
    }

    match state.item_service.search_items(&search_term).await {
        Ok(items) => {
            println!("Search returned {} items", items.len());
            Ok(Json(ApiResponse::success(items)))
        }
        Err(e) => {
            println!("Error searching items: {}", e);
            Ok(Json(ApiResponse::error(e.to_string())))
        }
    }
}

#[handler]
async fn get_bundles(Data(state): Data<&AppState>) -> poem::Result<Json<ApiResponse<Vec<Bundle>>>> {
    println!("GET /api/bundles");
    match state.bundle_service.get_all_bundles().await {
        Ok(bundles) => {
            println!("Successfully retrieved {} bundles", bundles.len());
            Ok(Json(ApiResponse::success(bundles)))
        }
        Err(e) => {
            println!("Error retrieving bundles: {}", e);
            Ok(Json(ApiResponse::error(e.to_string())))
        }
    }
}

#[handler]
async fn get_bundle_items(
    Path(bundle_id): Path<i32>,
    Data(state): Data<&AppState>,
) -> poem::Result<Json<ApiResponse<Vec<BundleItem>>>> {
    println!("GET /api/bundles/{}/items", bundle_id);
    match state.bundle_service.get_bundle_items(bundle_id).await {
        Ok(items) => {
            println!(
                "Successfully retrieved {} items for bundle {}",
                items.len(),
                bundle_id
            );
            Ok(Json(ApiResponse::success(items)))
        }
        Err(e) => {
            println!("Error retrieving bundle items: {}", e);
            Ok(Json(ApiResponse::error(e.to_string())))
        }
    }
}

#[handler]
async fn get_progress(
    Data(state): Data<&AppState>,
) -> poem::Result<Json<ApiResponse<Vec<UserProgress>>>> {
    println!("GET /api/progress");
    match state.progress_service.get_progress().await {
        Ok(progress) => {
            println!("Successfully retrieved {} progress entries", progress.len());
            Ok(Json(ApiResponse::success(progress)))
        }
        Err(e) => {
            println!("Error retrieving progress: {}", e);
            Ok(Json(ApiResponse::error(e.to_string())))
        }
    }
}

#[handler]
async fn mark_completed(
    Json(req): Json<ProgressRequest>,
    Data(state): Data<&AppState>,
) -> poem::Result<Json<ApiResponse<()>>> {
    println!(
        "POST /api/progress/complete - bundle_item_id: {}",
        req.bundle_item_id
    );
    match state
        .progress_service
        .mark_completed(req.bundle_item_id)
        .await
    {
        Ok(_) => {
            println!(
                "Successfully marked item {} as completed",
                req.bundle_item_id
            );
            Ok(Json(ApiResponse::success(())))
        }
        Err(e) => {
            println!("Error marking item as completed: {}", e);
            Ok(Json(ApiResponse::error(e.to_string())))
        }
    }
}

#[handler]
async fn mark_incomplete(
    Json(req): Json<ProgressRequest>,
    Data(state): Data<&AppState>,
) -> poem::Result<Json<ApiResponse<()>>> {
    println!(
        "POST /api/progress/incomplete - bundle_item_id: {}",
        req.bundle_item_id
    );
    match state
        .progress_service
        .mark_incomplete(req.bundle_item_id)
        .await
    {
        Ok(_) => {
            println!(
                "Successfully marked item {} as incomplete",
                req.bundle_item_id
            );
            Ok(Json(ApiResponse::success(())))
        }
        Err(e) => {
            println!("Error marking item as incomplete: {}", e);
            Ok(Json(ApiResponse::error(e.to_string())))
        }
    }
}

#[handler]
async fn serve_index() -> poem::Result<poem::Response> {
    println!("Serving index page");
    let html_content = include_str!("../../webapp.html");

    Ok(poem::Response::builder()
        .header("content-type", "text/html")
        .body(html_content))
}

#[handler]
async fn serve_css() -> poem::Result<poem::Response> {
    let css_content = include_str!("../../../src-ui/styles/main.css");
    Ok(poem::Response::builder()
        .header("content-type", "text/css")
        .body(css_content))
}

#[handler]
async fn serve_js() -> poem::Result<poem::Response> {
    let js_content = include_str!("../../../src-ui/scripts/web-api.js");
    Ok(poem::Response::builder()
        .header("content-type", "application/javascript")
        .body(js_content))
}

#[handler]
async fn serve_main_js() -> poem::Result<poem::Response> {
    let js_content = include_str!("../../../src-ui/scripts/main.js");
    Ok(poem::Response::builder()
        .header("content-type", "application/javascript")
        .body(js_content))
}

#[handler]
async fn serve_junimo_icon() -> poem::Result<poem::Response> {
    let icon_bytes = include_bytes!("../../../src-ui/assets/junimo.png");
    Ok(poem::Response::builder()
        .header("content-type", "image/png")
        .header("cache-control", "public, max-age=31536000") // Cache for 1 year
        .body(icon_bytes.as_slice()))
}

#[tokio::main]
async fn main() -> Result<()> {
    dotenv().ok();

    println!("🍄 Starting Junimo Web Server...");

    // Initialize database connection
    let db = database::init().await?;
    println!("✓ Database connection established");

    // Run migrations
    database::migrate(&db).await?;
    println!("✓ Database migrations completed");

    // Test database connection
    let item_count: (i64,) = sqlx::query_as("SELECT COUNT(*) FROM items")
        .fetch_one(&db)
        .await?;
    println!("✓ Found {} items in database", item_count.0);

    // Initialize services
    let app_state = AppState {
        item_service: ItemService::new(db.clone()),
        bundle_service: BundleService::new(db.clone()),
        progress_service: ProgressService::new(db.clone()),
    };
    println!("✓ Services initialized");

    // Create API routes
    let api = Route::new()
        .at("/items", get(get_items))
        .at("/items/search", get(search_items))
        .at("/bundles", get(get_bundles))
        .at("/bundles/:bundle_id/items", get(get_bundle_items))
        .at("/progress", get(get_progress))
        .at("/progress/complete", post(mark_completed))
        .at("/progress/incomplete", post(mark_incomplete))
        .data(app_state);

    // Create main app with static file serving
    let app = Route::new()
        .at("/", get(serve_index))
        .nest("/api", api)
        .at("/static/styles/main.css", get(serve_css))
        .at("/static/scripts/web-api.js", get(serve_js))
        .at("/static/scripts/main.js", get(serve_main_js))
        .at("/assets/junimo.png", get(serve_junimo_icon))
        .with(Cors::new());

    println!("🚀 Server starting on http://localhost:3000");
    println!("📱 Visit: http://localhost:3000");

    Server::new(TcpListener::bind("0.0.0.0:3000"))
        .run(app)
        .await?;

    Ok(())
}
