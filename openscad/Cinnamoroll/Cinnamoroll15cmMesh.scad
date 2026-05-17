// シナモロール：緯度線・経度線メッシュモデル
// 頭の最大幅：約100mm (10cm)

$fn = 24; // 線の滑らかさ
line_radius = 0.5; // メッシュの線の太さ
lat_steps = 12;    // 緯度線の分割数
lon_steps = 18;    // 経度線の分割数

// 汎用メッシュ球体モジュール
module mesh_ellipsoid(size_vec, lats, lons, wire_r) {
    scale(size_vec) {
        // 緯度線 (Horizontal lines)
        for (i = [1 : lats - 1]) {
            lat_angle = (i * 180 / lats) - 90;
            r = cos(lat_angle);
            z = sin(lat_angle);
            translate([0, 0, z])
                rotate_extrude()
                    translate([r, 0, 0])
                        circle(r = wire_r / max(size_vec)); 
        }
        
        // 経度線 (Vertical lines)
        for (i = [0 : lons - 1]) {
            lon_angle = i * 360 / lons;
            rotate([0, 0, lon_angle])
                rotate([90, 0, 0])
                    rotate_extrude()
                        translate([1, 0, 0])
                            circle(r = wire_r / max(size_vec));
        }
    }
}

// --- 各パーツの配置 ---

// 1. 頭 (Head) - 横幅100mm
color("white")
translate([0, 0, 0])
    mesh_ellipsoid([50, 40, 35], lat_steps, lon_steps, line_radius);

// 2. 耳 (Ears) - 長くて垂れている
color("white") {
    // 右耳
    translate([45, 0, 10])
        rotate([0, 20, 0])
            mesh_ellipsoid([40, 15, 10], 8, 12, line_radius);
    // 左耳
    translate([-45, 0, 10])
        rotate([0, -20, 0])
            mesh_ellipsoid([40, 15, 10], 8, 12, line_radius);
}

// 3. 体 (Body) - 頭より小さめ
color("white")
translate([0, 0, -45])
    mesh_ellipsoid([25, 20, 25], 10, 12, line_radius);

// 4. 手 (Hands)
color("white") {
    translate([20, -10, -40])
        mesh_ellipsoid([8, 8, 8], 6, 8, line_radius);
    translate([-20, -10, -40])
        mesh_ellipsoid([8, 8, 8], 6, 8, line_radius);
}

// 5. 足 (Feet)
color("white") {
    translate([12, 0, -70])
        mesh_ellipsoid([10, 12, 8], 6, 8, line_radius);
    translate([-12, 0, -70])
        mesh_ellipsoid([10, 12, 8], 6, 8, line_radius);
}

// (オプション) 目と口 - これもメッシュで表現
color("blue") {
    // 目
    translate([15, -38, 0])
        mesh_ellipsoid([4, 2, 6], 4, 6, 0.3);
    translate([-15, -38, 0])
        mesh_ellipsoid([4, 2, 6], 4, 6, 0.3);
}