const spaRoutes = {
  home: { file: "index.html", title: "UTH Store - Trang Chủ" },
  index: { file: "index.html", title: "UTH Store - Trang Chủ" },
  products: { file: "products.html", title: "UTH Store - Sản phẩm" },
  "product-detail": {
    file: "product-detail.html",
    title: "UTH Store - Chi tiết sản phẩm",
  },
  cart: { file: "cart.html", title: "UTH Store - Giỏ hàng" },
  contact: { file: "contact.html", title: "UTH Store - Liên hệ" },
  policy: { file: "policy.html", title: "UTH Store - Chính sách" },
  admin: { file: "admin.html", title: "UTH Store - Admin" },
  login: { file: "login.html", title: "UTH Store - Đăng nhập" },
};

const contentContainer = document.getElementById("page-content");
const parser = new DOMParser();
const initialHomeContent = contentContainer?.innerHTML || "";
const initialTitle = document.title;

function parseHashRoute(hash) {
  const routePart = hash.startsWith("#") ? hash.slice(1) : hash;
  const [route, query] = routePart.split("?");
  return {
    route: route || "home",
    query: query || "",
  };
}

function getRouteFromHref(href) {
  if (!href || href === "#") return null;
  if (href.startsWith("#")) {
    const [route, query] = href.slice(1).split("?");
    if (!route) return null;
    return {
      route,
      query: query || "",
    };
  }
  try {
    const url = new URL(href, window.location.href);
    if (url.origin !== window.location.origin) return null;
    const file = url.pathname.split("/").pop();
    if (!file) return { route: "home", query: url.searchParams.toString() };
    const route = file.replace(".html", "");
    return spaRoutes[route]
      ? { route, query: url.searchParams.toString() }
      : null;
  } catch {
    return null;
  }
}

async function loadRoute(hash) {
  if (!contentContainer) return;

  const { route } = parseHashRoute(hash);
  const routeInfo = spaRoutes[route] || spaRoutes.home;

  // Animate content fade-out
  contentContainer.classList.add("opacity-0");
  await new Promise((resolve) => setTimeout(resolve, 120));

  if (route === "home") {
    contentContainer.innerHTML = initialHomeContent;
    document.title = initialTitle;
  } else {
    try {
      const response = await fetch(routeInfo.file, { cache: "no-store" });
      if (!response.ok) {
        throw new Error("Fetch failed");
      }
      const html = await response.text();
      const doc = parser.parseFromString(html, "text/html");
      const main = doc.querySelector("main");
      const pageTitle = doc.querySelector("title")?.textContent;
      contentContainer.innerHTML = main ? main.innerHTML : html;
      document.title = pageTitle || routeInfo.title;
    } catch (err) {
      contentContainer.innerHTML = `
        <div class="min-h-[60vh] flex items-center justify-center px-6 py-20 text-center">
          <div>
            <p class="text-xl font-semibold text-on-surface">Không thể tải trang. Vui lòng thử lại.</p>
            <p class="text-stone-500 mt-3">Lỗi: ${err.message}</p>
          </div>
        </div>
      `;
      document.title = routeInfo.title;
    }
  }

  // Scroll and fade in
  window.scrollTo({ top: 0, behavior: "smooth" });
  setTimeout(() => contentContainer.classList.remove("opacity-0"), 10);

  // Re-run dynamic page scripts after content load
  if (typeof window.initCart === "function") window.initCart();
  if (typeof window.renderNewArrivals === "function")
    window.renderNewArrivals();
  if (typeof window.setupEventListeners === "function")
    window.setupEventListeners();
}

function handleNavigationClick(event) {
  const anchor = event.target.closest("a");
  if (!anchor) return;

  const href = anchor.getAttribute("href");
  const routeInfo = getRouteFromHref(href);
  if (!routeInfo) return;

  event.preventDefault();
  const hash =
    routeInfo.route === "home"
      ? "#home"
      : `#${routeInfo.route}${routeInfo.query ? `?${routeInfo.query}` : ""}`;
  if (window.location.hash !== hash) {
    window.location.hash = hash;
  } else {
    loadRoute(hash);
  }
}

window.addEventListener("hashchange", () => loadRoute(window.location.hash));
document.addEventListener("click", handleNavigationClick);
document.addEventListener("DOMContentLoaded", () => {
  const initialHash = window.location.hash || "#home";
  if (!contentContainer) return;

  // Ensure route classes exist for fade animation
  contentContainer.classList.add("transition-opacity", "duration-300");
  loadRoute(initialHash);
});
