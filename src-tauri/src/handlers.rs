use crate::models::{Bundle, BundleItem, Item, UserProgress};
use crate::AppState;
use tauri::State;

#[tauri::command]
pub async fn get_items(state: State<'_, AppState>) -> Result<Vec<Item>, String> {
    println!("get_items handler called");
    let result = state.item_service.get_all_items().await;
    match &result {
        Ok(items) => println!("Successfully retrieved {} items", items.len()),
        Err(e) => println!("Error retrieving items: {}", e),
    }
    result.map_err(|e| e.to_string())
}

#[tauri::command]
pub async fn search_items(query: String, state: State<'_, AppState>) -> Result<Vec<Item>, String> {
    state
        .item_service
        .search_items(&query)
        .await
        .map_err(|e| e.to_string())
}

#[tauri::command]
pub async fn get_bundles(state: State<'_, AppState>) -> Result<Vec<Bundle>, String> {
    println!("get_bundles handler called");
    let result = state.bundle_service.get_all_bundles().await;
    match &result {
        Ok(bundles) => println!("Successfully retrieved {} bundles", bundles.len()),
        Err(e) => println!("Error retrieving bundles: {}", e),
    }
    result.map_err(|e| e.to_string())
}

#[tauri::command]
pub async fn get_bundle_items(
    bundleId: i32,
    state: State<'_, AppState>,
) -> Result<Vec<BundleItem>, String> {
    println!("get_bundle_items handler called for bundleId: {}", bundleId);
    let result = state.bundle_service.get_bundle_items(bundleId).await;
    match &result {
        Ok(items) => println!(
            "Successfully retrieved {} bundle items for bundle {}",
            items.len(),
            bundleId
        ),
        Err(e) => println!(
            "Error retrieving bundle items for bundle {}: {}",
            bundleId, e
        ),
    }
    result.map_err(|e| e.to_string())
}

#[tauri::command]
pub async fn mark_item_completed(
    bundleItemId: i32,
    state: State<'_, AppState>,
) -> Result<(), String> {
    println!(
        "mark_item_completed handler called for bundleItemId: {}",
        bundleItemId
    );
    let result = state.progress_service.mark_completed(bundleItemId).await;
    match &result {
        Ok(_) => println!(
            "Successfully marked bundle item {} as completed",
            bundleItemId
        ),
        Err(e) => println!(
            "Error marking bundle item {} as completed: {}",
            bundleItemId, e
        ),
    }
    result.map_err(|e| e.to_string())
}

#[tauri::command]
pub async fn mark_item_incomplete(
    bundleItemId: i32,
    state: State<'_, AppState>,
) -> Result<(), String> {
    println!(
        "mark_item_incomplete handler called for bundleItemId: {}",
        bundleItemId
    );
    let result = state.progress_service.mark_incomplete(bundleItemId).await;
    match &result {
        Ok(_) => println!(
            "Successfully marked bundle item {} as incomplete",
            bundleItemId
        ),
        Err(e) => println!(
            "Error marking bundle item {} as incomplete: {}",
            bundleItemId, e
        ),
    }
    result.map_err(|e| e.to_string())
}

#[tauri::command]
pub async fn get_progress(state: State<'_, AppState>) -> Result<Vec<UserProgress>, String> {
    println!("get_progress handler called");
    let result = state.progress_service.get_progress().await;
    match &result {
        Ok(progress) => println!("Successfully retrieved {} progress entries", progress.len()),
        Err(e) => println!("Error retrieving progress: {}", e),
    }
    result.map_err(|e| e.to_string())
}
