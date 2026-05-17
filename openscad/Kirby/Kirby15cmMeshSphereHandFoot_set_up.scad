// --- 設定パラメータ ---
body_diameter = 150;     // 本体の直径
line_thickness = 1.8;    // 印刷強度のため少し太めを推奨
lat_steps = 5;           // 緯線の数（片半球）
lon_steps = 12;          // 経線の数
$fn = 40;

body_radius = body_diameter / 2;

// --- 3Dプリント用レイアウト ---

// 1. 北半球ユニット (中心に配置)
translate([-body_radius - 10, 0, 0])
half_sphere_unit(is_north = true);

// 2. 南半球ユニット (北半球と同じ向きで配置)
translate([body_radius + 10, 0, 0])
half_sphere_unit(is_north = false);

// 3. 手 (2個)
hand_r = 22;
translate([-body_radius, -body_radius - 30, hand_r]) mesh_sphere_gen(hand_r, 3, 8, line_thickness);
translate([0, -body_radius - 30, hand_r])            mesh_sphere_gen(hand_r, 3, 8, line_thickness);

// 4. 足 (2個)
foot_r = 25;
translate([body_radius, -body_radius - 45, foot_r]) 
    scale([1.8, 1.2, 1.0]) mesh_sphere_gen(foot_r, 3, 8, line_thickness / 1.5);
translate([body_radius * 2.5, -body_radius - 45, foot_r]) 
    scale([1.8, 1.2, 1.0]) mesh_sphere_gen(foot_r, 3, 8, line_thickness / 1.5);

// --- モジュール定義 ---

// 半球ユニット（メッシュ、スポーク、地軸の半分を含む）
module half_sphere_unit(is_north = true) {
    // 南半球の場合は、断面を下にするために180度回転させる
    rotate([is_north ? 0 : 180, 0, 0])
    // 南半球が回転した際、Z+側にくるように調整
    translate([0, 0, is_north ? 0 : 0]) 
    union() {
        // メッシュ半球
        intersection() {
            mesh_sphere_gen(body_radius, lat_steps, lon_steps, line_thickness);
            if (is_north) {
                translate([-200, -200, 0]) cube([400, 400, 200]); // 上半分
            } else {
                translate([-200, -200, -200]) cube([400, 400, 200]); // 下半分
            }
        }
        
        // 内部構造（スポーク）
        for (i = [0 : lon_steps - 1]) {
            angle = i * (360 / lon_steps);
            rotate([0, 90, angle])
            cylinder(h = body_radius, d = line_thickness);
        }
        
        // 地軸（半分）
        if (is_north) {
            // 中心から北極へ
            cylinder(h = body_radius, d = line_thickness);
        } else {
            // 中心から南極へ
            translate([0, 0, -body_radius])
            cylinder(h = body_radius, d = line_thickness);
        }
    }
}

// 共通メッシュ生成モジュール
module mesh_sphere_gen(r, lats, lons, thick) {
    // 経線
    for (i = [0 : lons - 1]) {
        rotate([0, 0, i * (180 / lons)])
        rotate([90, 0, 0])
        thin_ring(r, thick);
    }
    // 緯線
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

// リング生成モジュール
module thin_ring(r, thickness) {
    if (r > thickness/2) {
        rotate_extrude()
        translate([r, 0, 0])
        circle(d = thickness);
    }
}