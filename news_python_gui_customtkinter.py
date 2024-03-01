
import requests
import customtkinter as ctk
from tkinter import Canvas, Frame, Label, Toplevel
import webbrowser
from PIL import Image, ImageTk
from io import BytesIO
import threading

ctk.set_appearance_mode("Light")  # Can be "System", "Dark", or "Light"
ctk.set_default_color_theme("blue")  # Several themes available
number_of_articles = 20  # Specify the number of articles you want to fetch

class NewsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("News App")
        self.root.geometry("800x600")

        # Container frame for category label, dropdown, and search button
        self.container_frame = ctk.CTkFrame(master=root)
        self.container_frame.pack(pady=20)

        # Adding a label for the category dropdown inside the container frame
        self.label_category = ctk.CTkLabel(master=self.container_frame, text=" Category:")
        self.label_category.pack(side="left", padx=(0, 10))  # Add some padding to separate from the dropdown

        # Category selection dropdown inside the container frame
        self.category = ctk.CTkComboBox(master=self.container_frame,
                                        values=["business", "entertainment", "general", "health", "science", "sports",
                                                "technology"])
        self.category.pack(side="left")
        self.category.set("general")  # default value

        # Search button next to the dropdown inside the container frame
        self.search_button = ctk.CTkButton(master=self.container_frame, text="Search", command=self.fetch_news)
        self.search_button.pack(side="left", padx=(10, 0))  # Add some padding to separate from the dropdown

        # Centering the container frame
        self.container_frame.pack_configure(anchor="center")

        self.canvas = Canvas(root)
        self.canvas.pack(side="left", fill="both", expand=True)

        self.scrollbar = ctk.CTkScrollbar(root, command=self.canvas.yview)
        self.scrollbar.pack(side="right", fill="y")

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.frame = Frame(self.canvas)
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.frame, anchor="nw")

        self.fetch_news()

    def on_category_change(self, event=None):
        # Optionally, automatically fetch news on category change or leave it to the search button
        pass

    def fetch_news(self):
        # Clear existing news cards
        for widget in self.frame.winfo_children():
            widget.destroy()

        api_key = 'API KEY'  # Replace 'your_api_key_here' with your actual NewsAPI key
        selected_category = self.category.get()
        url = f'https://newsapi.org/v2/top-headlines?country=us&category={selected_category}&pageSize={number_of_articles}&apiKey={api_key}'

        response = requests.get(url)
        if response.status_code == 200:
            articles = response.json()['articles']
            for article in articles:
                self.root.after(0, lambda article=article: self.display_news(article))
        else:
            print("Failed to retrieve news articles")

    def display_news(self, article):
        # Check if any of the required fields are missing or None
        title = article.get('title')
        description = article.get('description')
        url = article.get('url')  # URL of the article
        image_url = article.get('urlToImage')

        # If any of the required fields are missing or None, skip this article
        if not all([title, description, url, image_url]):
            return

        card = ctk.CTkFrame(master=self.frame, corner_radius=10)
        card.pack(padx=20, pady=10, fill='x', expand=True)

        # Placeholder for the image
        label_image_placeholder = Label(card)
        label_image_placeholder.pack(padx=10, pady=(5, 0), fill='x')

        # Since we've already fetched these, we can directly use them without default values
        if image_url:
            threading.Thread(target=lambda: self.fetch_and_display_image(image_url, label_image_placeholder),
                             daemon=True).start()

        label_title = ctk.CTkLabel(master=card, text=title, font=("Roboto Medium", 16), wraplength=700)
        label_title.pack(pady=(10, 5), padx=10)

        label_description = ctk.CTkLabel(master=card, text=description, font=("Roboto", 14), wraplength=700,
                                         fg_color=None)
        label_description.pack(pady=5, padx=10)

        # Button to open the URL
        button_read_more = ctk.CTkButton(master=card, text="Read More", command=lambda url=url: self.open_url(url))
        button_read_more.pack(pady=5)

    def fetch_and_display_image(self, url, label_placeholder):
        try:
            response = requests.get(url)
            response.raise_for_status()  # Check if the request was successful
            img_data = BytesIO(response.content)
            img = Image.open(img_data)
            img = img.resize((label_placeholder.winfo_width(), 500), Image.ANTIALIAS)  # Resize image
            photo = ImageTk.PhotoImage(img)

            # Update the placeholder with the actual image
            self.root.after(0, lambda: label_placeholder.config(image=photo))
            label_placeholder.image = photo  # Keep a reference
        except Exception as e:
            print(f"Failed to load image: {e}")

    def open_url(self, url):
        webbrowser.open(url)

if __name__ == "__main__":
    root = ctk.CTk()
    app = NewsApp(root)
    root.mainloop()
