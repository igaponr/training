// --- 設定パラメータ ---
diameter = 150;          // 直径 (150mm = 15cm)
line_thickness = 1.0;    // 線の太さ
lat_steps = 6;           // 緯線の数（片半球あたり）
lon_steps = 12;          // 経線の数（全周）
$fn = 40;                // 滑らかさ

radius = diameter / 2;

// 全体の実行
union() {
    mesh_sphere();       // メッシュ球体
    internal_structure(); // 追加された内部直線
}

module mesh_sphere() {
    // --- 経線 (Longitudinal lines) ---
    for (i = [0 : lon_steps - 1]) {
        rotate([0, 0, i * (180 / lon_steps)])
        rotate([90, 0, 0])
        thin_ring(radius, line_thickness);
    }

    // --- 緯線 (Latitudinal lines) ---
    // 赤道
    thin_ring(radius, line_thickness);
    
    // 北半球・南半球の緯線
    if (lat_steps > 0) {
        for (i = [1 : lat_steps]) {
            lat_angle = i * (90 / (lat_steps + 1));
            lat_radius = radius * cos(lat_angle);
            lat_height = radius * sin(lat_angle);
            
            translate([0, 0, lat_height])
            thin_ring(lat_radius, line_thickness);
            
            translate([0, 0, -lat_height])
            thin_ring(lat_radius, line_thickness);
        }
    }
}

module internal_structure() {
    // 1. 北極から南極への直線 (地軸)
    // シリンダーを中心(center=true)に配置することでZ軸方向に上下に伸びます
    color("red") // 構造を見やすくするために色を変える場合はここを有効に
    cylinder(h = diameter, d = line_thickness, center = true);

    // 2. 赤道と経線の交点から中心への直線
    // 経線の数に合わせて放射状に配置
    for (i = [0 : lon_steps - 1]) {
        angle = i * (360 / lon_steps);
        rotate([0, 90, angle]) // Z軸中心に回転させ、X軸方向に倒して配置
        cylinder(h = radius, d = line_thickness);
    }
}

// 共通パーツ：細いリングを作るモジュール
module thin_ring(r, thickness) {
    if (r > thickness/2) {
        rotate_extrude()
        translate([r, 0, 0])
        circle(d = thickness);
    }
}