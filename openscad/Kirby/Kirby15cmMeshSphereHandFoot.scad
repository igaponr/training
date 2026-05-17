// --- 設定パラメータ ---
body_diameter = 150;     // 本体の直径 (150mm)
line_thickness = 1.2;    // 線の太さ
lat_steps = 6;           // 緯線の数（片半球）
lon_steps = 12;          // 経線の数（全周）
$fn = 30;                // 滑らかさ（重い場合は数値を下げてください）

body_radius = body_diameter / 2;

// 全体の実行
union() {
    // 1. 本体メッシュ
    mesh_sphere_gen(body_radius, lat_steps, lon_steps, line_thickness);
    
    // 2. 内部構造 (地軸と赤道スポーク) - 本体のみに適用
    internal_structure(body_radius, lon_steps, line_thickness);
    
    // 3. メッシュの手足
    kirby_mesh_limbs();
}

// --- 手足を配置するモジュール ---
module kirby_mesh_limbs() {
    hand_r = 22;      // 手の半径
    foot_r = 25;      // 足の基本半径（あとでスケールして楕円にする）

    // 手 (右)
    rotate([0, -30, 40])
    translate([body_radius + hand_r * 0.3, 0, 0])
    mesh_sphere_gen(hand_r, 3, 8, line_thickness);

    // 手 (左)
    rotate([0, -30, 140])
    translate([body_radius + hand_r * 0.3, 0, 0])
    mesh_sphere_gen(hand_r, 3, 8, line_thickness);

    // 足 (右)
    translate([35, 15, -body_radius + 12])
    rotate([0, 10, -20])
    scale([1.8, 1.2, 1.0]) // 足を楕円形に引き伸ばす
    mesh_sphere_gen(foot_r, 3, 8, line_thickness);

    // 足 (左)
    translate([-35, 15, -body_radius + 12])
    rotate([0, 10, 200])
    scale([1.8, 1.2, 1.0]) // 足を楕円形に引き伸ばす
    mesh_sphere_gen(foot_r, 3, 8, line_thickness);
}

// --- 汎用メッシュ球体モジュール ---
// r:半径, lats:緯線分割, lons:経線分割, thick:線の太さ
module mesh_sphere_gen(r, lats, lons, thick) {
    // 経線 (縦)
    for (i = [0 : lons - 1]) {
        rotate([0, 0, i * (180 / lons)])
        rotate([90, 0, 0])
        thin_ring(r, thick);
    }
    // 緯線 (横)
    thin_ring(r, thick); // 赤道
    if (lats > 0) {
        for (i = [1 : lats]) {
            lat_angle = i * (90 / (lats + 1));
            lat_r = r * cos(lat_angle);
            lat_z = r * sin(lat_angle);
            
            translate([0, 0, lat_z]) thin_ring(lat_r, thick);
            translate([0, 0, -lat_z]) thin_ring(lat_r, thick);
        }
    }
}

// --- 内部構造 (本体用) ---
module internal_structure(r, lons, thick) {
    // 地軸 (北極-南極)
    cylinder(h = r * 2, d = thick, center = true);

    // 赤道から中心へのスポーク
    for (i = [0 : lons - 1]) {
        angle = i * (360 / lons);
        rotate([0, 90, angle])
        cylinder(h = r, d = thick);
    }
}

// --- リング生成用共通モジュール ---
module thin_ring(r, thickness) {
    if (r > thickness/2) {
        rotate_extrude()
        translate([r, 0, 0])
        circle(d = thickness);
    }
}