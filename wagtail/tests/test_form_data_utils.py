from django.test import SimpleTestCase

from wagtail.test.utils.form_data import querydict_from_html


class TestQueryDictFromHTML(SimpleTestCase):
    html = """
    <form id="personal-details">
        <input type="hidden" name="csrfmiddlewaretoken" value="Z783HTL5Bc2J54WhAtEeR3eefM1FBkq0EbTfNnYnepFGuJSOfvosFvwjeKYtMwFr">
        <input type="hidden" name="no_value_input">
        <input type="hidden" value="no name input">
        <div class="mt-8 max-w-md">
            <div class="grid grid-cols-1 gap-6">
                <label class="block">
                    <span class="text-gray-700">Full name</span>
                    <input type="text" name="name" value="Jane Doe" class="mt-1 block w-full" placeholder="">
                </label>
                <label class="block">
                    <span class="text-gray-700">Email address</span>
                    <input type="email" name="email" class="mt-1 block w-full" value="jane@example.com" placeholder="name@example.com">
                </label>
            </div>
        </div>
    </form>
    <form id="event-details">
        <div class="mt-8 max-w-md">
            <div class="grid grid-cols-1 gap-6">
                <label class="block">
                    <span class="text-gray-700">When is your event?</span>
                    <input type="date" name="date" class="mt-1 block w-full" value="2023-01-01">
                </label>
                <label class="block">
                    <span class="text-gray-700">What type of event is it?</span>
                    <select name="event_type" class="block w-full mt-1">
                        <option value="corporate">Corporate event</option>
                        <option value="wedding">Wedding</option>
                        <option value="birthday">Birthday</option>
                        <option value="other" selected>Other</option>
                    </select>
                </label>
                <label class="block">
                    <span class="text-gray-700">What age groups is it suitable for?</span>
                    <select name="ages" class="block w-full mt-1" multiple>
                        <option>Infants</option>
                        <option>Children</option>
                        <option>Teenagers</option>
                        <option selected>18-30</option>
                        <option selected>30-50</option>
                        <option>50-70</option>
                        <option>70+</option>
                    </select>
                </label>
            </div>
        </div>
    </form>
    <form id="market-research">
        <div class="mt-8 max-w-md">
            <div class="grid grid-cols-1 gap-6">
                <fieldset class="block">
                    <legend>How many pets do you have?</legend>
                    <div class="radio-list">
                        <div class="radio">
                            <label>
                                <input type="radio" name="pets" value="0" />
                                None
                            </label>
                        </div>
                        <div class="radio">
                            <label>
                                <input type="radio" name="pets" value="1" />
                                One
                            </label>
                        </div>
                        <div class="radio">
                            <label>
                                <input type="radio" name="pets" value="2" checked />
                                Two
                            </label>
                        </div>
                        <div class="radio">
                            <label>
                                <input type="radio" name="pets" value="3+" />
                                Three or more
                            </label>
                        </div>
                    </div>
                </fieldset>
                <fieldset class="block">
                    <legend>Which two colours do you like best?</legend>
                    <div class="checkbox-list">
                        <div class="checkbox">
                            <label>
                                <input type="checkbox" name="colours" value="cyan">
                                Cyan
                            </label>
                        </div>
                        <div class="checkbox">
                            <label>
                                <input type="checkbox" name="colours" value="magenta" checked />
                                Magenta
                            </label>
                        </div>
                        <div class="checkbox">
                            <label>
                                <input type="checkbox" name="colours" value="yellow" />
                                Yellow
                            </label>
                        </div>
                        <div class="checkbox">
                            <label>
                                <input type="checkbox" name="colours" value="black" checked />
                                Black
                            </label>
                        </div>
                        <div class="checkbox">
                            <label>
                                <input type="checkbox" name="colours" value="white" />
                                White
                            </label>
                        </div>
                    </div>
                </fieldset>
                <label class="block">
                    <span class="text-gray-700">Tell us what you love</span>
                    <textarea name="love" class="mt-1 block w-full" rows="3">Comic books</textarea>
                </label>
            </div>
        </div>
    </form>
    """

    personal_details = [
        ("no_value_input", [""]),
        ("name", ["Jane Doe"]),
        ("email", ["jane@example.com"]),
    ]

    event_details = [
        ("date", ["2023-01-01"]),
        ("event_type", ["other"]),
        ("ages", ["18-30", "30-50"]),
    ]

    market_research = [
        ("pets", ["2"]),
        ("colours", ["magenta", "black"]),
        ("love", ["Comic books"]),
    ]

    def test_html_only(self):
        # data should be extracted from the 'first' form by default
        result = querydict_from_html(self.html)
        self.assertEqual(list(result.lists()), self.personal_details)

    def test_include_csrf(self):
        result = querydict_from_html(self.html, exclude_csrf=False)
        expected_result = [
            (
                "csrfmiddlewaretoken",
                ["Z783HTL5Bc2J54WhAtEeR3eefM1FBkq0EbTfNnYnepFGuJSOfvosFvwjeKYtMwFr"],
            )
        ] + self.personal_details
        self.assertEqual(list(result.lists()), expected_result)

    def test_form_index(self):
        for index, expected_data in (
            (0, self.personal_details),
            ("2", self.market_research),
            (1, self.event_details),
        ):
            result = querydict_from_html(self.html, form_index=index)
            self.assertEqual(list(result.lists()), expected_data)

    def test_form_id(self):
        for id, expected_data in (
            ("event-details", self.event_details),
            ("personal-details", self.personal_details),
            ("market-research", self.market_research),
        ):
            result = querydict_from_html(self.html, form_id=id)
            self.assertEqual(list(result.lists()), expected_data)

    def test_invalid_form_id(self):
        with self.assertRaises(ValueError):
            querydict_from_html(self.html, form_id="invalid-id")

    def test_invalid_index(self):
        with self.assertRaises(ValueError):
            querydict_from_html(self.html, form_index=5)





    def test_no_form_id_or_index(self):
        # Quando nenhum form_id ou form_index é fornecido, o primeiro formulário deve ser usado
        result = querydict_from_html(self.html)
        self.assertEqual(list(result.lists()), self.personal_details)

    def test_invalid_form_index(self):
        # Verificar se um ValueError é lançado ao fornecer um índice de formulário inválido
        with self.assertRaises(ValueError):
            querydict_from_html(self.html, form_index=5)

    def test_multiple_forms(self):
        # Verificar se é possível extrair dados de um formulário específico quando há vários formulários no HTML
        result = querydict_from_html(self.html, form_id='event-details')
        self.assertEqual(list(result.lists()), self.event_details)

    def test_exclude_csrf(self):
        # Verificar se é possível excluir o token CSRF dos dados extraídos
        result = querydict_from_html(self.html, exclude_csrf=True)
        expected_result = self.personal_details  # Não inclui o token CSRF
        self.assertEqual(list(result.lists()), expected_result)

    def test_input_types(self):
        # Verificar se os diferentes tipos de campos de entrada são tratados corretamente
        html = """
        <form>
            <input type="text" name="text_input" value="Text Value">
            <input type="password" name="password_input" value="Password Value">
            <input type="checkbox" name="checkbox_input" value="Checkbox Value" checked>
            <input type="radio" name="radio_input" value="Radio Value" checked>
            <input type="hidden" name="hidden_input" value="Hidden Value">
            <textarea name="textarea_input">Textarea Value</textarea>
        </form>
        """
        expected_result = [
            ('text_input', ['Text Value']),
            ('password_input', ['Password Value']),
            ('checkbox_input', ['Checkbox Value']),
            ('radio_input', ['Radio Value']),
            ('hidden_input', ['Hidden Value']),
            ('textarea_input', ['Textarea Value']),
        ]
        result = querydict_from_html(html)
        self.assertEqual(list(result.lists()), expected_result)

    def test_select_field(self):
        # Verificar se os campos de seleção são tratados corretamente
        html = """
        <form>
            <select name="select_field">
                <option value="option1">Option 1</option>
                <option value="option2" selected>Option 2</option>
                <option value="option3">Option 3</option>
            </select>
            <select name="multiple_select_field" multiple>
                <option value="option1" selected>Option 1</option>
                <option value="option2">Option 2</option>
                <option value="option3" selected>Option 3</option>
            </select>
        </form>
        """
        expected_result = [
            ('select_field', ['option2']),
            ('multiple_select_field', ['option1', 'option3']),
        ]
        result = querydict_from_html(html)
        self.assertEqual(list(result.lists()), expected_result)

    def test_fieldset(self):
        # Verificar se os campos dentro de um fieldset são tratados corretamente
        html = """
        <form>
            <fieldset>
                <legend>Fieldset 1</legend>
                <input type="text" name="input1" value="Value 1">
                <input type="text" name="input2" value="Value 2">
            </fieldset>
            <fieldset>
                <legend>Fieldset 2</legend>
                <input type="text" name="input3" value="Value 3">
                <input type="text" name="input4" value="Value 4">
            </fieldset>
        </form>
        """
        expected_result = [
            ('input1', ['Value 1']),
            ('input2', ['Value 2']),
            ('input3', ['Value 3']),
            ('input4', ['Value 4']),
        ]
        result = querydict_from_html(html)
        self.assertEqual(list(result.lists()), expected_result)

    def test_empty_html(self):
        # Verificar se um ValueError é lançado ao fornecer um HTML vazio
        with self.assertRaises(ValueError):
            querydict_from_html('')

    def test_form_without_inputs(self):
        # Verificar se um ValueError é lançado quando um formulário não contém nenhum campo de entrada
        html = '<form></form>'
        with self.assertRaises(ValueError):
            querydict_from_html(html)
