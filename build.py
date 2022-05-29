import json
import random
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
import shutil

random.seed("scrapfly")


class Builder:
    def __init__(self, basedir: Path, baseurl="http://127.0.0.1:8000/") -> None:
        self.tpl_env = Environment(loader=FileSystemLoader("templates"))
        self.tpl_env.globals["base_url"] = baseurl
        self.out_dir = basedir
        self.data_dir = Path("data")
        self.static_dir = Path("static")
        shutil.rmtree(self.out_dir, ignore_errors=True)

    def render_static(self):
        shutil.copytree(self.static_dir, self.out_dir / "static")

    def render_index(self):
        index_tpl = self.tpl_env.get_template("index.html")
        with open(self.out_dir / "index.html", "w") as f:
            f.write(index_tpl.render())

    def render_products(self, page_size=8):
        with open(self.data_dir / "products.json") as f:
            products = json.loads(f.read())
        products = [random.choice(products) for i in range(50)]
        product_tpl = self.tpl_env.get_template("product.html")
        product_dir = self.out_dir / "product"
        product_dir.mkdir()
        for product in products:
            (product_dir / f"{product['id']}.html").write_text(
                product_tpl.render(product=product)
            )

        products_tpl = self.tpl_env.get_template("products.html")
        product_batches = [
            products[i : i + page_size] for i in range(0, len(products), page_size)
        ]
        for i, batch in enumerate(product_batches):
            rendered = products_tpl.render(
                page_number=i + 1, products=batch, page_total=len(product_batches), result_total=len(products)
            )
            # page_data = {
            #     "paging": {"page": i + 1, "has_more": i + 1 < len(product_batches)},
            #     "results": batch,
            #     "_rendered": [product_preview_ptl.render(product=p) for p in batch],
            # }
            # (self.out_dir / f"products-{i+1}.json").write_text(
            #     json.dumps(page_data, indent=2)
            # )
            (self.out_dir / f"products-{i+1}.html").write_text(rendered)

        # SPA
        # first page
        products_spa_tpl = self.tpl_env.get_template("products-spa.html")
        (self.out_dir / "products-spa.html").write_text(
            products_spa_tpl.render(products=product_batches[0], page_number=1)
        )
        # other pages as htmx renders
        product_out = self.out_dir / "product-previews/"
        product_out.mkdir(exist_ok=True)
        for i, batch in enumerate(product_batches[1:], start=2):
            page = self.tpl_env.get_template("products-spa-page.html").render(
                products=batch,
                page_number=i
            )
            (product_out / f"{i}.html").write_text(page)


if __name__ == "__main__":
    builder = Builder(Path("output"))
    builder.render_static()
    builder.render_index()
    builder.render_products()
