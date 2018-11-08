# Kano Wand
Easily use the Kano Harry Potter Wand in Python

### Demos available at the [kano-wand-demos repo](https://github.com/GammaGames/kano-wand-demos)

- [Kano Wand](#kano-wand)
        - [Demos available at the kano-wand-demos repo](#demos-available-at-the-kano-wand-demos-repo)
    - [Usage:](#usage)
    - [Classes](#classes)
        - [Wand](#wand)
            - [Methods](#methods)
        - [Shoppe](#shoppe)
            - [Methods](#methods-1)
    - [FAQ](#faq)

## Usage:
First, you'll want to create a `Shoppe`. It handles scanning for new wands and will return an array of wand objects. There are a few different ways to use the wands:

1. Use the wands returned by scanning
    * Create a shoppe and start to scan, returning an array of found wands
    * For each wand, call methods like `set_led` or `vibrate` on the wand object
    * Call the `on` method with an event type (`"position"`, `"button"`, etc) and a callback function to process events
    * Call the `off` method with a callback's id (returned from `on`) to remove a callback

2. Use a custom wand class
    * Create a class that inherits from `Wand`
    * Override the `post_connect` method in the new class to call methods and subscribe to events
    * Override methods (such as `on_position` or `on_button`) to use the data from the wand
    * Pass the class to the Shoppe using the `wand_class` argument on creation
    * Start scanning, and let the program run while it uses your custom wand class

3. Use a combination of the two
    * Create a custom class that inherits from wand
    * Add event callbacks with the `on` method
    * Override methods (such as `on_position` or `on_button`) to process events
    * Remove event callbacks with the `off` method, passing `continue_notifications=True` to prevent the notification thread from stopping

## Classes

### Wand

#### Methods

### Shoppe

#### Methods

## FAQ

1. What operating systems will the module run on?

    * Currently it only runs on linux, as it is based on bluepy (which only supports linux)

2. The
